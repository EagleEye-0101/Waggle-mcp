import * as fs from "fs/promises";
import * as https from "https";
import * as path from "path";
import * as vscode from "vscode";
import {
  assetFileNameForCurrentPlatform,
  buildAssetNameToPlatformKeyMap,
  platformAssetKey,
  type PlatformAssetKey
} from "./platform";

export interface BundleMetadata {
  version: string;
  repository: string;
  assets: Record<string, string>;
}

const DEFAULT_REPO = "Abhigyan-Shekhar/Waggle-mcp";
const NETWORK_TIMEOUT_MS = 60_000;

export class BinaryResolver {
  constructor(private readonly context: vscode.ExtensionContext) {}

  private config(): vscode.WorkspaceConfiguration {
    return vscode.workspace.getConfiguration("waggle");
  }

  private cacheRoot(): string {
    return path.join(this.context.globalStorageUri.fsPath, "waggle-bin");
  }

  async resolveCommandPath(): Promise<string> {
    const method = this.config().get<string>("installMethod", "binary");
    const configured = this.config().get<string>("commandPath", "waggle-mcp");
    if (method === "pipx") {
      return configured;
    }
    if (await this.hasCachedBinary()) {
      return await this.cachedBinaryPath();
    }
    if (path.isAbsolute(configured)) {
      try {
        await fs.access(configured);
        return configured;
      } catch {
        // fall through to download
      }
    }
    return this.ensureBinary();
  }

  async hasCachedBinary(): Promise<boolean> {
    try {
      await fs.access(await this.cachedBinaryPath());
      return true;
    } catch {
      return false;
    }
  }

  private async cachedBinaryPathForVersion(version: string): Promise<string> {
    const assetName = assetFileNameForCurrentPlatform();
    return path.join(this.cacheRoot(), version, assetName);
  }

  private async cachedBinaryPath(): Promise<string> {
    const version = await this.resolveRequestedVersion();
    return this.cachedBinaryPathForVersion(version);
  }

  async ensureBinary(): Promise<string> {
    const metadata = await this.fetchBundleMetadata();
    const destPath = await this.cachedBinaryPathForVersion(metadata.version);
    try {
      await fs.access(destPath);
      return destPath;
    } catch {
      // download below
    }

    const assetName = metadata.assets[platformAssetKey()];
    if (!assetName) {
      throw new Error(`Release v${metadata.version} has no asset for ${platformAssetKey()}`);
    }

    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Waggle",
        cancellable: false
      },
      async () => {
        await fs.mkdir(path.dirname(destPath), { recursive: true });
        const url = `https://github.com/${metadata.repository}/releases/download/v${metadata.version}/${assetName}`;
        await this.downloadFile(url, destPath);
        if (process.platform !== "win32") {
          await fs.chmod(destPath, 0o755);
        }
      }
    );

    return destPath;
  }

  private async resolveRequestedVersion(): Promise<string> {
    const override = this.config().get<string>("binaryVersion", "").trim();
    if (override) {
      return override;
    }
    return this.context.extension.packageJSON.version as string;
  }

  private async fetchBundleMetadata(): Promise<BundleMetadata> {
    const repo = this.config().get<string>("binaryReleaseRepo", DEFAULT_REPO).trim() || DEFAULT_REPO;
    const requestedVersion = await this.resolveRequestedVersion();

    const fromRelease = await this.tryFetchReleaseMetadata(repo, requestedVersion);
    if (fromRelease) {
      return fromRelease;
    }

    if (this.config().get<boolean>("binaryAllowLatestFallback", false)) {
      const latest = await this.tryFetchLatestMetadata(repo);
      if (latest) {
        return latest;
      }
    }

    throw new Error(
      `No GitHub release v${requestedVersion} with Waggle binaries for ${platformAssetKey()}. ` +
        "Set waggle.commandPath, waggle.installMethod to pipx, enable waggle.binaryAllowLatestFallback, or wait for a maintainer release."
    );
  }

  private async tryFetchReleaseMetadata(repo: string, version: string): Promise<BundleMetadata | undefined> {
    try {
      const release = await this.fetchJson<{
        tag_name: string;
        assets: { name: string }[];
      }>(`https://api.github.com/repos/${repo}/releases/tags/v${version}`);
      return this.metadataFromRelease(release, repo);
    } catch {
      return undefined;
    }
  }

  private async tryFetchLatestMetadata(repo: string): Promise<BundleMetadata | undefined> {
    try {
      const release = await this.fetchJson<{
        tag_name: string;
        assets: { name: string }[];
      }>(`https://api.github.com/repos/${repo}/releases/latest`);
      return this.metadataFromRelease(release, repo);
    } catch {
      return undefined;
    }
  }

  private metadataFromRelease(
    release: { tag_name: string; assets: { name: string }[] },
    repo: string
  ): BundleMetadata {
    const version = release.tag_name.replace(/^v/, "");
    const nameToKey = buildAssetNameToPlatformKeyMap();
    const assets: Partial<Record<PlatformAssetKey, string>> = {};

    for (const asset of release.assets) {
      const key = nameToKey.get(asset.name);
      if (key) {
        assets[key] = asset.name;
      }
    }

    const platform = platformAssetKey();
    const expectedName = assetFileNameForCurrentPlatform();
    const actualName = assets[platform];
    if (!actualName) {
      throw new Error(
        `Release v${version} is missing ${expectedName} for ${platform}. Available: ${release.assets.map((a) => a.name).join(", ") || "(none)"}`
      );
    }

    return { version, repository: repo, assets: assets as Record<string, string> };
  }

  private fetchJson<T>(url: string): Promise<T> {
    return new Promise((resolve, reject) => {
      const headers: Record<string, string> = {
        Accept: "application/vnd.github+json",
        "User-Agent": "waggle-vscode-extension"
      };
      const request = https.get(url, { headers }, (response) => {
        if (response.statusCode === 302 || response.statusCode === 301) {
          const location = response.headers.location;
          if (location) {
            void this.fetchJson<T>(location).then(resolve, reject);
            return;
          }
        }
        if ((response.statusCode ?? 0) >= 400) {
          reject(new Error(`GitHub API ${response.statusCode ?? 0} for ${url}`));
          return;
        }
        const chunks: Buffer[] = [];
        response.on("data", (chunk: Buffer) => chunks.push(chunk));
        response.on("end", () => {
          try {
            resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")) as T);
          } catch (error) {
            reject(error);
          }
        });
      });
      request.on("error", reject);
      request.setTimeout(NETWORK_TIMEOUT_MS, () => {
        request.destroy();
        reject(new Error(`GitHub API request timed out for ${url}`));
      });
    });
  }

  private downloadFile(url: string, destPath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = https.get(url, { headers: { "User-Agent": "waggle-vscode-extension" } }, (response) => {
        if (response.statusCode === 302 || response.statusCode === 301) {
          const location = response.headers.location;
          if (!location) {
            reject(new Error(`Redirect without location for ${url}`));
            return;
          }
          void this.downloadFile(location, destPath).then(resolve, reject);
          return;
        }
        if ((response.statusCode ?? 0) >= 400) {
          reject(new Error(`Download failed (${response.statusCode ?? 0}) for ${url}`));
          return;
        }
        const chunks: Buffer[] = [];
        response.on("data", (chunk: Buffer) => chunks.push(chunk));
        response.on("end", () => {
          void fs.writeFile(destPath, Buffer.concat(chunks)).then(() => resolve(), reject);
        });
      });
      request.on("error", reject);
      request.setTimeout(NETWORK_TIMEOUT_MS, () => {
        request.destroy();
        reject(new Error(`Binary download timed out for ${url}`));
      });
    });
  }
}
