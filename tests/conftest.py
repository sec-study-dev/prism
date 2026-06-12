"""Shared pytest fixtures for PRISM tests."""
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def ir_schema_path(repo_root: Path) -> Path:
    return repo_root / "ir-schema" / "meta-ir.schema.json"


@pytest.fixture(scope="session")
def ir_schema(ir_schema_path: Path) -> dict:
    return json.loads(ir_schema_path.read_text())


@pytest.fixture(scope="session")
def protocol_schema_path(repo_root: Path) -> Path:
    return repo_root / "corpus" / "protocol-metadata.schema.json"


@pytest.fixture(scope="session")
def protocol_schema(protocol_schema_path: Path) -> dict:
    return json.loads(protocol_schema_path.read_text())


@pytest.fixture(scope="session")
def benchmark_schema_path(repo_root: Path) -> Path:
    return repo_root / "benchmark" / "benchmark-event.schema.json"


@pytest.fixture(scope="session")
def benchmark_schema(benchmark_schema_path: Path) -> dict:
    return json.loads(benchmark_schema_path.read_text())


@pytest.fixture(scope="session")
def mechanism_graph_schema_path(repo_root: Path) -> Path:
    return repo_root / "ir-schema" / "mechanism-graph.schema.json"


@pytest.fixture(scope="session")
def mechanism_graph_schema(mechanism_graph_schema_path: Path) -> dict:
    return json.loads(mechanism_graph_schema_path.read_text())
