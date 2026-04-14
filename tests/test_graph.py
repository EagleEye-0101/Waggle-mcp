from __future__ import annotations

from pathlib import Path

import networkx as nx
import numpy as np

from waggle.graph import MemoryGraph
from waggle.models import NodeType, RelationType


class FakeEmbeddingModel:
    def embed(self, text: str) -> np.ndarray:
        vector = np.zeros(8, dtype=np.float32)
        for token in text.lower().split():
            index = sum(ord(character) for character in token) % len(vector)
            vector[index] += 1.0
        norm = np.linalg.norm(vector)
        if norm == 0.0:
            return vector
        return vector / norm

    def to_bytes(self, embedding: np.ndarray) -> bytes:
        return embedding.astype(np.float32).tobytes()

    def from_bytes(self, data: bytes) -> np.ndarray:
        return np.frombuffer(data, dtype=np.float32)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        if a_norm == 0.0 or b_norm == 0.0:
            return 0.0
        return float(np.dot(a, b) / (a_norm * b_norm))


def make_graph(tmp_path: Path) -> MemoryGraph:
    return MemoryGraph(tmp_path / "memory.db", FakeEmbeddingModel())


def test_add_query_and_related(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    project = graph.add_node(
        label="FastAPI Project",
        content="User is building a FastAPI backend service",
        node_type=NodeType.ENTITY,
        tags=["backend"],
    ).node
    preference = graph.add_node(
        label="Python Preference",
        content="User strongly prefers Python for backend work",
        node_type=NodeType.PREFERENCE,
    ).node
    graph.add_edge(
        source_id=project.id,
        target_id=preference.id,
        relationship=RelationType.RELATES_TO,
    )

    result = graph.query(query="python backend", max_nodes=5, max_depth=2)
    labels = {node.label for node in result.nodes}
    assert "FastAPI Project" in labels
    assert "Python Preference" in labels
    assert len(result.edges) == 1

    related = graph.get_related(node_id=project.id, max_depth=1)
    related_labels = {node.label for node in related.nodes}
    assert related_labels == {"FastAPI Project", "Python Preference"}


def test_update_delete_and_stats(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    node = graph.add_node(
        label="Deployment Note",
        content="Initial deployment uses SQLite",
        node_type=NodeType.NOTE,
    ).node
    updated = graph.update_node(
        node_id=node.id,
        content="Deployment now uses SQLite and nightly backups",
        tags=["ops", "database"],
    )
    assert updated.tags == ["ops", "database"]
    assert "nightly backups" in updated.content

    stats = graph.get_stats()
    assert stats.total_nodes == 1
    assert stats.node_type_breakdown["note"] == 1

    deleted = graph.delete_node(node_id=node.id)
    assert deleted.id == node.id
    assert graph.get_stats().total_nodes == 0


def test_exact_duplicate_nodes_are_reused_and_tags_are_merged(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    first = graph.add_node(
        label="Python Preference",
        content="User prefers Python for backend work",
        node_type=NodeType.PREFERENCE,
        tags=["python"],
    )
    second = graph.add_node(
        label="Python Preference",
        content="User prefers Python for backend work",
        node_type=NodeType.PREFERENCE,
        tags=["backend"],
        source_prompt="duplicate check",
    )

    assert first.created is True
    assert second.created is False
    assert second.node.id == first.node.id
    assert second.dedup_reason == "exact_content"
    assert second.node.tags == ["python", "backend"]
    assert graph.get_stats().total_nodes == 1


def test_semantic_duplicate_nodes_reuse_existing_entry(tmp_path: Path) -> None:
    graph = MemoryGraph(
        tmp_path / "semantic-memory.db",
        FakeEmbeddingModel(),
        dedup_similarity_threshold=0.75,
        dedup_same_label_threshold=0.75,
    )
    first = graph.add_node(
        label="FastAPI Project",
        content="User is building a FastAPI backend service",
        node_type=NodeType.ENTITY,
    )
    second = graph.add_node(
        label="FastAPI Project",
        content="User is building a FastAPI backend app service",
        node_type=NodeType.ENTITY,
    )

    assert first.created is True
    assert second.created is False
    assert second.node.id == first.node.id
    assert second.dedup_reason == "same_label_high_similarity"


def test_entity_resolution_reuses_acronym_matches(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    first = graph.add_node(
        label="Large Language Model",
        content="Large language model memory is important for this project",
        node_type=NodeType.ENTITY,
    )
    second = graph.add_node(
        label="LLM",
        content="LLM memory is important for this project",
        node_type=NodeType.ENTITY,
    )

    assert first.created is True
    assert second.created is False
    assert second.node.id == first.node.id
    assert second.dedup_reason == "acronym_entity_match"


def test_query_ranking_uses_label_lexical_overlap(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    graph.add_node(
        label="JWT Auth",
        content="Authentication subsystem for the service",
        node_type=NodeType.CONCEPT,
    )
    graph.add_node(
        label="Session Storage",
        content="Stores session data for authenticated users",
        node_type=NodeType.CONCEPT,
    )

    result = graph.query(query="jwt", max_nodes=2, max_depth=0)

    assert result.nodes[0].label == "JWT Auth"


def test_decompose_and_store_creates_nodes_and_edges(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)

    result = graph.decompose_and_store(
        content="- User prefers Python for backend work\n- Project uses FastAPI for the API",
        context="Backend preferences and stack",
    )

    labels = {node.label for node in result.nodes}
    assert "Backend preferences and stack" in labels
    assert any("User prefers Python" in node.content for node in result.nodes)
    assert any("Project uses FastAPI" in node.content for node in result.nodes)
    assert len(result.edges) >= 2


def test_export_and_import_backup_round_trip(tmp_path: Path) -> None:
    source = make_graph(tmp_path / "source")
    imported = make_graph(tmp_path / "target")
    first = source.add_node(
        label="Backup Node",
        content="This node should survive a backup round trip",
        node_type=NodeType.NOTE,
    ).node
    second = source.add_node(
        label="Backup Concept",
        content="This concept is connected to the backup node",
        node_type=NodeType.CONCEPT,
    ).node
    source.add_edge(
        source_id=first.id,
        target_id=second.id,
        relationship=RelationType.RELATES_TO,
    )

    backup = source.export_graph_backup(output_path=tmp_path / "backup.json")
    imported_result = imported.import_graph_backup(input_path=backup.output_path)

    assert backup.node_count == 2
    assert backup.edge_count == 1
    assert imported_result.nodes_created == 2
    assert imported_result.edges_created == 1
    assert imported.get_stats().total_nodes == 2
    assert imported.get_stats().total_edges == 1


def test_export_graph_html_creates_visualization_file(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    first = graph.add_node(
        label="Visualization Project",
        content="The memory graph should support HTML export.",
        node_type=NodeType.CONCEPT,
    ).node
    second = graph.add_node(
        label="Visualization Edge",
        content="The exported graph should include connected nodes.",
        node_type=NodeType.FACT,
    ).node
    graph.add_edge(
        source_id=second.id,
        target_id=first.id,
        relationship=RelationType.PART_OF,
    )

    output_path = graph.export_graph_html(output_path=tmp_path / "graph.html", include_physics=False)
    html = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert "Visualization Project" in html
    assert "Visualization Edge" in html
    assert "part_of" in html


def test_conflict_detection_creates_contradiction_edge(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    first = graph.add_node(
        label="REST Preference",
        content="User prefers REST APIs for backend services",
        node_type=NodeType.PREFERENCE,
    )
    second = graph.add_node(
        label="GraphQL Preference",
        content="User prefers GraphQL APIs for backend services",
        node_type=NodeType.PREFERENCE,
    )

    assert second.created is True
    assert second.conflicts
    related = graph.get_related(node_id=second.node.id, max_depth=1)
    assert any(edge.relationship == RelationType.CONTRADICTS for edge in related.edges)
    assert first.node.id in {node.id for node in related.nodes}


def test_load_graph_preserves_edge_attributes(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    a = graph.add_node(label="A", content="A", node_type=NodeType.FACT).node
    b = graph.add_node(label="B", content="B", node_type=NodeType.FACT).node

    graph.add_edge(
        source_id=a.id,
        target_id=b.id,
        relationship=RelationType.CONTRADICTS,
        weight=0.9,
    )

    with graph._connect() as connection:
        g = graph._load_graph(connection, node_ids=[a.id, b.id])

    edge_data = g.edges[a.id, b.id]
    assert edge_data["relationship"] == "contradicts"
    assert edge_data["weight"] == 0.9
    assert edge_data["metadata"] == {}


def test_expand_node_depths_prioritizes_stronger_relations(tmp_path: Path) -> None:
    graph_store = make_graph(tmp_path)
    graph = nx.DiGraph()
    graph.add_edge("seed", "conflict", relationship="contradicts", weight=1.0)
    graph.add_edge("seed", "support", relationship="depends_on", weight=1.0)
    graph.add_edge("seed", "weak", relationship="similar_to", weight=1.0)

    ordered = graph_store._expand_node_depths(graph, ["seed"], max_depth=1)

    keys = list(ordered.keys())

    # seed must always be first
    assert keys[0] == "seed"

    # Now check PRIORITY ORDER
    conflict_idx = keys.index("conflict")
    support_idx = keys.index("support")
    weak_idx = keys.index("weak")

    assert conflict_idx < support_idx < weak_idx


def test_expand_node_depths_prunes_weak_paths(tmp_path: Path) -> None:
    graph_store = make_graph(tmp_path)
    graph = nx.DiGraph()
    graph.add_edge("seed", "a", relationship="depends_on", weight=1.0)
    graph.add_edge("a", "b", relationship="similar_to", weight=1.0)

    ordered = graph_store._expand_node_depths(
        graph,
        ["seed"],
        max_depth=2,
        min_priority=0.25,
    )

    assert ordered["seed"] == 0
    assert ordered["a"] == 1
    assert "b" not in ordered


def test_observe_conversation_extracts_nodes(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)

    result = graph.observe_conversation(
        user_message="I prefer Python for backend work. Can we use FastAPI?",
        assistant_response="Let's use FastAPI and store the API in src/server.py.",
    )

    assert result.created_count >= 3
    labels = {node.label for node in result.stored_nodes}
    assert "I prefer Python for backend work" in labels
    assert "Can we use FastAPI?" in labels
    assert "src/server.py" in labels


def test_observe_conversation_extracts_clean_database_and_auth_facts(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)

    result = graph.observe_conversation(
        user_message=(
            "We chose PostgreSQL over MySQL because MySQL replication has been painful. "
            "We are using FastAPI for the backend. JWT tokens expire in 15 minutes."
        ),
        assistant_response=(
            "Understood. I'll remember that PostgreSQL was chosen, the reason was MySQL replication pain, "
            "FastAPI is the backend, and JWT expiry is 15 minutes."
        ),
    )

    labels = {node.label for node in result.stored_nodes}
    assert "Database decision" in labels
    assert "Backend framework" in labels
    assert "JWT expiry" in labels
    assert "MySQL replication has been painful" in labels
    assert "I'll remember that PostgreSQL was chosen," not in labels
    assert "FastAPI" not in labels


def test_observe_conversation_creates_database_contradiction_edges(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    graph.observe_conversation(
        user_message="We chose PostgreSQL over MySQL because MySQL replication has been painful.",
        assistant_response="Understood.",
    )

    result = graph.observe_conversation(
        user_message="The team is more familiar with MySQL, so we may switch to MySQL.",
        assistant_response="Understood. I'll note that.",
    )

    assert result.conflicts
    decision_node = next(node for node in result.stored_nodes if node.label == "Database decision")
    related = graph.get_related(node_id=decision_node.id, max_depth=1)
    assert any(edge.relationship == RelationType.CONTRADICTS for edge in related.edges)


def test_query_supports_temporal_latest_and_oldest_bias(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    graph.add_node(
        label="Auth v1",
        content="Auth architecture originally used JWT sessions",
        node_type=NodeType.CONCEPT,
    )
    graph.add_node(
        label="Auth v2",
        content="Auth architecture now uses rotating JWT tokens",
        node_type=NodeType.CONCEPT,
    )

    latest = graph.query(query="latest auth architecture", max_nodes=1, max_depth=0)
    originally = graph.query(query="originally auth architecture", max_nodes=1, max_depth=0)

    assert latest.nodes[0].label == "Auth v2"
    assert originally.nodes[0].label == "Auth v1"


def test_graph_diff_and_prime_context(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    graph.add_node(
        label="Project Alpha",
        content="Project Alpha uses FastAPI",
        node_type=NodeType.ENTITY,
        tags=["alpha"],
    )
    note = graph.add_node(
        label="Alpha Decision",
        content="We decided to use SQLite for Alpha",
        node_type=NodeType.DECISION,
        tags=["alpha"],
    ).node
    graph.update_node(node_id=note.id, tags=["alpha", "updated"])

    diff = graph.graph_diff(since="24h")
    prime = graph.prime_context(project="alpha")

    assert diff.added_nodes
    assert prime.nodes
    assert any("alpha" in node.tags for node in prime.nodes)


def test_get_topics_returns_clusters(tmp_path: Path) -> None:
    graph = make_graph(tmp_path)
    graph.add_node(
        label="Auth REST",
        content="User prefers REST APIs for auth",
        node_type=NodeType.PREFERENCE,
        tags=["auth", "api"],
    )
    graph.add_node(
        label="Auth JWT",
        content="Project uses JWT authentication",
        node_type=NodeType.CONCEPT,
        tags=["auth"],
    )
    graph.add_node(
        label="Database Neo4j",
        content="Project uses Neo4j for memory storage",
        node_type=NodeType.ENTITY,
        tags=["database"],
    )

    topics = graph.get_topics()

    assert topics.total_clusters >= 1
    assert topics.clusters[0].nodes
