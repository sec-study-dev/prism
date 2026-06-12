"""Stage 1 configuration constants."""
from pathlib import Path

# Model selection
PASS1_MODEL = "claude-sonnet-4-6"
PASS2_MODEL = "claude-sonnet-4-6"
POC_MODEL = "claude-sonnet-4-6"

# Retry limits (spec §6 §7 §8)
CONSENSUS_MAX_ROUNDS = 5
PASS2_MAX_ATTEMPTS = 3
POC_MAX_ATTEMPTS = 3

# Token / cost
PER_PROTOCOL_INPUT_BUDGET = 2_000_000
PER_PROTOCOL_OUTPUT_BUDGET = 400_000
HARD_USD_BUDGET = 500.0

# Snapshot blocks (Tier-A unified, matches metadata.json)
ETH_SNAPSHOT_BLOCK = 22_500_000
BSC_SNAPSHOT_BLOCK = 50_000_000

# Pipeline version (goes into sidecar metrics)
PIPELINE_VERSION = "stage1-v1.0"

# Source blob bounds (chars) — keeps per-call prompt and token spend bounded
# while still feeding the LLM substantial real deployed source.
SOURCE_PER_CONTRACT_CHARS = 80_000
SOURCE_TOTAL_CHARS = 200_000

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MECHANISM_DB = REPO_ROOT / "mechanism-db"
SOURCE_CACHE_ROOT = REPO_ROOT / ".prism-cache" / "source"
CORPUS_TIER_A = REPO_ROOT / "corpus" / "tier-a" / "protocols"
IR_SCHEMA_PATH = REPO_ROOT / "ir-schema" / "meta-ir.schema.json"
SIDECAR_SCHEMA_PATH = REPO_ROOT / "ir-schema" / "sidecar-metrics.schema.json"
SEED_TAGS_PATH = REPO_ROOT / "ir-schema" / "seed-tags.md"
