"""Stage 2 interface normalization: meta-IR mechanism -> canonical resource ports."""
from __future__ import annotations

import re

from .model import Ports
from .resources import Resource

_PRICE_RE = re.compile(r"share|exchange[\s_-]?rate|redemption|price[\s_-]?per[\s_-]?share", re.I)
_ORACLE_RE = re.compile(r"oracle|price|feed", re.I)
_BALANCE_RE = re.compile(r"balance|amount|transfer|deposit|withdraw", re.I)


def _protocol(ir: dict) -> str:
    return ir["id"].split(".", 1)[0]


def _token_refs(ir: dict) -> list[str]:
    return [d["ref"] for d in ir.get("deps", []) if d["kind"] == "token-standard"]


def _dedup(rs: list[Resource]) -> list[Resource]:
    seen, out = set(), []
    for r in rs:
        key = (r.kind, r.id, r.origin)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def normalize(ir: dict) -> Ports:
    protocol = _protocol(ir)
    tags = set(ir.get("tags", []))
    token_refs = _token_refs(ir)
    produces: list[Resource] = []
    consumes: list[Resource] = []

    # deps: stable cross-protocol join keys (consumed)
    for i, d in enumerate(ir.get("deps", [])):
        origin = f"deps[{i}]"
        if d["kind"] == "oracle":
            consumes.append(Resource("oracle", d["ref"], origin=origin))
        elif d["kind"] == "flashloan-provider":
            consumes.append(Resource("flashloan", d["ref"], origin=origin))
        elif d["kind"] == "token-standard":
            consumes.append(Resource("token", d["ref"], origin=origin))

    # a flashloan mechanism produces the loaned token capital
    if "flashloan" in tags:
        for ref in token_refs:
            produces.append(Resource("token", ref, origin="tags:flashloan"))

    # state writes -> produced resources
    for i, w in enumerate(ir.get("state_writes", [])):
        origin = f"state_writes[{i}]"
        purpose = w.get("purpose", "")
        stype = w.get("solidity_type")
        qual = f"{protocol}.{w['contract']}.{w['variable']}"
        if _PRICE_RE.search(purpose):
            produces.append(Resource("price", qual, stype, origin))
        elif _BALANCE_RE.search(purpose) and token_refs:
            for ref in token_refs:
                produces.append(Resource("token", ref, stype, origin))
        else:
            produces.append(Resource("protocol-state", qual, stype, origin))

    # state reads -> consumed resources
    for i, r in enumerate(ir.get("state_reads", [])):
        origin = f"state_reads[{i}]"
        purpose = r.get("purpose", "")
        stype = r.get("solidity_type")
        qual = f"{protocol}.{r['contract']}.{r['variable']}"
        if _PRICE_RE.search(purpose):
            consumes.append(Resource("price", qual, stype, origin))
        elif _ORACLE_RE.search(purpose):
            consumes.append(Resource("oracle", qual, stype, origin))
        else:
            consumes.append(Resource("protocol-state", qual, stype, origin))

    # preconditions that check a token balance -> precondition-origin token consume
    for i, c in enumerate(ir.get("preconditions", [])):
        if c["kind"] == "balance-check" and token_refs:
            for ref in token_refs:
                consumes.append(Resource("token", ref, origin=f"preconditions[{i}]"))

    return Ports(produces=_dedup(produces), consumes=_dedup(consumes))
