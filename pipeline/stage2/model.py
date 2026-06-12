"""Shared dataclasses for the Stage 2 mechanism graph."""
from __future__ import annotations

from dataclasses import dataclass, field

from .resources import Resource


@dataclass
class Ports:
    produces: list[Resource] = field(default_factory=list)
    consumes: list[Resource] = field(default_factory=list)


@dataclass
class Node:
    id: str
    chain: str
    protocol: str
    tags: list[str]
    ports: Ports
    ir: dict


@dataclass
class Edge:
    src: str
    dst: str
    type: str
    directed: bool
    chain: str
    shared_resources: list[Resource] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
