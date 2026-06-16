#!/usr/bin/env python3
"""
MAGI — Multi-agent Adversarial Grounded Inquiry
Orchestrator engine v1.0

Drives the Three Gifts dialectical spiral through mimo-v2.5-pro delegates.
Designed for Hermes Agent — uses delegate_task for parallel dispatch.

Usage (from Hermes session):
    python3 lib/magi.py "topic"
    python3 lib/magi.py --dry-run "topic"
"""

import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


# ─── Constants ───────────────────────────────────────────────────────────────

MAGI_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = MAGI_ROOT / "prompts"
AUDIT_BASE = Path("/tmp/magi-audit")

MAX_SPIRAL_CYCLES = 3
MAX_CONVERGENCE_RESTARTS = 2
DELEGATE_TIMEOUT = 300  # seconds
TOTAL_TIMEOUT = 1800    # 30 minutes


class GiftType(Enum):
    GOLD = "gold"
    FRANKINCENSE = "frankincense"
    MYRRH = "myrrh"


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class GiftOutput:
    """Output from a single Gift analysis."""
    gift: GiftType
    phase: str
    content: str
    claims: list = field(default_factory=list)
    confidence_high: list = field(default_factory=list)
    confidence_medium: list = field(default_factory=list)
    confidence_low: list = field(default_factory=list)
    blind_spots: list = field(default_factory=list)
    timestamp: str = ""
    duration_seconds: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ThreeGifts:
    """Container for all three Gift outputs."""
    gold: Optional[GiftOutput] = None
    frankincense: Optional[GiftOutput] = None
    myrrh: Optional[GiftOutput] = None

    def get(self, gift_type: GiftType) -> Optional[GiftOutput]:
        return {
            GiftType.GOLD: self.gold,
            GiftType.FRANKINCENSE: self.frankincense,
            GiftType.MYRRH: self.myrrh,
        }[gift_type]

    def set(self, gift_type: GiftType, output: GiftOutput):
        if gift_type == GiftType.GOLD:
            self.gold = output
        elif gift_type == GiftType.FRANKINCENSE:
            self.frankincense = output
        else:
            self.myrrh = output

    def all_present(self) -> bool:
        return all([self.gold, self.frankincense, self.myrrh])


@dataclass
class ConvergenceResult:
    """Result of the Manger gate evaluation."""
    converged: bool
    factual_score: float     # 0.0-1.0
    interpretive_score: float
    risk_score: float
    overall_score: float     # weighted sum
    failed_dimension: Optional[str] = None
    restart_focus: Optional[str] = None
    reasoning: str = ""


@dataclass
class Verdict:
    """Final output — The Revelation (Phase 4)."""
    topic: str
    verdict: str
    confidence_topology: list = field(default_factory=list)
    known_unknowns: list = field(default_factory=list)
    action_items: list = field(default_factory=list)
    dissent: list = field(default_factory=list)
    convergence_score: float = 0.0
    spiral_cycles: int = 0
    total_duration: float = 0.0
    phase_files: dict = field(default_factory=dict)


# ─── Prompt Templates ────────────────────────────────────────────────────────

def load_gift_prompt(gift_type: GiftType) -> str:
    """Load the prompt template for a specific Gift."""
    prompt_file = PROMPTS_DIR / f"{gift_type.value}.md"
    if prompt_file.exists():
        return prompt_file.read_text()
    return _default_gift_prompt(gift_type)


def _default_gift_prompt(gift_type: GiftType) -> str:
    """Fallback prompt if template file is missing."""
    prompts = {
        GiftType.GOLD: """You are GOLD (金 / Caspar) — the Gift of Precision.

Your epistemological stance: verification, ground truth, evidence.
Your question: "Is this TRUE? Can I verify it?"

RULES:
- Every claim must trace to a specific source (file:line, document, data point)
- Numbers must be exact — no rounding without disclosure
- If you cannot verify something, say so explicitly
- Do NOT speculate. Do NOT synthesize. VERIFY.

Output format:
## Verified Facts
[List each fact with source citation]

## Key Claims
[Each claim + evidence strength]

## Confidence Level
- High: [items you'd stake your reputation on]
- Medium: [items with supporting evidence but gaps]
- Low: [items with weak or single-source evidence]

## What I Cannot Determine
[Explicit blind spots]""",

        GiftType.FRANKINCENSE: """You are FRANKINCENSE (乳香 / Melchior) — the Gift of Context.

Your epistemological stance: synthesis, patterns, meaning.
Your question: "What does this MEAN? What patterns emerge?"

RULES:
- Look across all available data for recurring patterns
- Connect disparate findings into a coherent narrative
- Consider context that others might miss
- Do NOT just restate facts. SYNTHESIZE meaning.

Output format:
## Contextual Synthesis
[The big picture — what it all means together]

## Patterns Identified
[Recurring structures, trends, correlations]

## Cross-Domain Connections
[How this relates to adjacent fields]

## Narrative
[A coherent story that explains the data]

## What I Cannot Connect
[Gaps in the narrative]""",

        GiftType.MYRRH: """You are MYRRH (沒藥 / Balthasar) — the Gift of Risk.

Your epistemological stance: adversarial analysis, fragility, blind spots.
Your question: "Where does this BREAK? What are we not seeing?"

RULES:
- Systematically probe for weaknesses in the other analyses
- Identify failure modes, edge cases, and hidden assumptions
- Stress-test conclusions: under what conditions would they fail?
- Do NOT be contrarian for its own sake. Be CONSTRUCTIVELY adversarial.

Output format:
## Risk Map
[Categories of risk with severity and likelihood]

## Fragility Points
[Where the conclusion is weakest and why]

## Blind Spots Detected
[What the other analyses missed]

## Failure Conditions
[Specific scenarios where the conclusion breaks]

## Anti-Fragility Recommendations
[How to strengthen against identified risks]""",
    }
    return prompts[gift_type]


def build_spiral_review_prompt(
    reviewer_gift: GiftType,
    reviewee_gift: GiftType,
    reviewee_output: str,
    original_topic: str,
) -> str:
    """Build a Phase 2 (Journey) spiral review prompt."""
    lens = {
        GiftType.GOLD: "through the lens of VERIFICATION — check every claim for factual accuracy",
        GiftType.FRANKINCENSE: "through the lens of CONTEXT — synthesize what this means in the broader picture",
        GiftType.MYRRH: "through the lens of RISK — identify where this analysis breaks or has blind spots",
    }

    return f"""You are {reviewer_gift.value.upper()} reviewing {reviewee_gift.value.upper()}'s analysis.

Original topic: {original_topic}

Review the following analysis {lens[reviewer_gift]}.

=== {reviewee_gift.value.upper()}'s ANALYSIS ===
{reviewee_output}
=== END ===

Produce your review in the same format as your Phase 1 output, but focused on:
1. What {reviewee_gift.value.upper()} got RIGHT (from your perspective)
2. What {reviewee_gift.value.upper()} got WRONG or MISSED
3. NEW insights that emerge from applying your lens to their analysis
4. Updated confidence levels for the claims you reviewed"""


def build_manger_prompt(gifts: ThreeGifts, cycle: int) -> str:
    """Build the Manger (convergence) evaluation prompt for hm."""
    return f"""Evaluate convergence of the MAGI dialectical spiral (cycle {cycle}).

You are evaluating three Gift analyses for alignment:

=== GOLD ===
{gifts.gold.content if gifts.gold else "NOT AVAILABLE"}

=== FRANKINCENSE ===
{gifts.frankincense.content if gifts.frankincense else "NOT AVAILABLE"}

=== MYRRH ===
{gifts.myrrh.content if gifts.myrrh else "NOT AVAILABLE"}

Score each dimension (0.0 to 1.0):

1. FACTUAL (weight 0.4): Do all Gifts agree on verified facts?
2. INTERPRETIVE (weight 0.3): Is Frankincense's synthesis uncontested?
3. RISK (weight 0.3): Have Myrrh's risks been addressed?

Output format:
FACTUAL: [score]
INTERPRETIVE: [score]
RISK: [score]
OVERALL: [weighted sum]
CONVERGED: [YES if overall >= 0.7, NO otherwise]
FAILED_DIMENSION: [if not converged, which dimension failed worst]
RESTART_FOCUS: [if not converged, what specific question to focus on]"""


# ─── Utility ─────────────────────────────────────────────────────────────────

def topic_slug(topic: str) -> str:
    """Create a filesystem-safe slug from a topic string."""
    slug = topic.lower().strip()
    slug = "".join(c if c.isalnum() or c in "- " else "" for c in slug)
    slug = slug.replace(" ", "-")[:60]
    return slug or "untitled"


def ensure_audit_dir(topic: str) -> Path:
    """Create and return the audit directory for a topic."""
    audit_dir = AUDIT_BASE / topic_slug(topic)
    if audit_dir.exists():
        shutil.rmtree(audit_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir


def write_phase_file(audit_dir: Path, filename: str, content: str) -> Path:
    """Write a phase output file and return its path."""
    filepath = audit_dir / filename
    filepath.write_text(content)
    return filepath


def parse_manger(text: str) -> ConvergenceResult:
    """Parse hm's Manger evaluation into a structured result."""
    def extract_score(pattern: str) -> float:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
        return 0.5

    factual = extract_score(r"FACTUAL:\s*([\d.]+)")
    interpretive = extract_score(r"INTERPRETIVE:\s*([\d.]+)")
    risk = extract_score(r"RISK:\s*([\d.]+)")
    overall = factual * 0.4 + interpretive * 0.3 + risk * 0.3

    converged = overall >= 0.7
    if "CONVERGED: YES" in text.upper():
        converged = True
    elif "CONVERGED: NO" in text.upper():
        converged = False

    failed = None
    restart = None
    if not converged:
        scores = {"factual": factual, "interpretive": interpretive, "risk": risk}
        failed = min(scores, key=scores.get)
        match = re.search(r"RESTART_FOCUS:\s*(.+)", text, re.IGNORECASE)
        if match:
            restart = match.group(1).strip()

    return ConvergenceResult(
        converged=converged,
        factual_score=factual,
        interpretive_score=interpretive,
        risk_score=risk,
        overall_score=overall,
        failed_dimension=failed,
        restart_focus=restart,
        reasoning=text,
    )


def write_manifest(audit_dir: Path, verdict: Verdict):
    """Write the execution manifest."""
    manifest = {
        "topic": verdict.topic,
        "convergence_score": verdict.convergence_score,
        "spiral_cycles": verdict.spiral_cycles,
        "total_duration_seconds": verdict.total_duration,
        "timestamp": datetime.now().isoformat(),
        "phase_files": verdict.phase_files,
    }
    (audit_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False)
    )


# ─── Main (standalone mode — for testing) ────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MAGI Protocol Orchestrator")
    parser.add_argument("topic", help="The topic to analyze")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    args = parser.parse_args()

    print(f"MAGI Protocol v1.0")
    print(f"Topic: {args.topic}")
    print(f"Slug:  {topic_slug(args.topic)}")
    print(f"Audit: {AUDIT_BASE / topic_slug(args.topic)}")
    print()

    if args.dry_run:
        print("[DRY RUN] Would execute:")
        print(f"  Phase 0 · The Star      — hm decomposes problem, assigns Gifts")
        print(f"  Phase 1 · The Offering   — Gold + Frankincense + Myrrh (parallel)")
        print(f"  Phase 2 · The Journey    — dialectical spiral (up to 3 cycles)")
        print(f"  Phase 3 · The Manger     — convergence gate (≥0.7 = pass)")
        print(f"  Phase 4 · The Revelation       — final verdict with confidence topology")
        print()
        print("Note: This engine is designed to be driven by Hermes Agent.")
        print("For real execution, invoke from a Hermes session with 'magi [topic]'.")
    else:
        print("MAGI engine requires a Hermes Agent session for execution.")
        print("Use --dry-run to preview, or invoke from Hermes directly.")
