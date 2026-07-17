import sys, os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from __future__ import annotations
import argparse, csv, json, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def retrieve(question: str) -> list[dict]:

    raise NotImplementedError("Wire this to your Chroma retrieval call.")


def answer(question: str) -> str:

    raise NotImplementedError("Wire this to your Gemini answer call")


# CONFIGS

REFUSAL_SIGNALS = [
    "i don't have", "i do not have", "not in the", "isn't in the", "is not in the",
    "couldn't find", "could not find", "no information", "cannot find", 
    "don't have enough", "insufficient context", "not available in the course"
]

SOLUTION_LEAK_SIGNALS = ["```"]

SOURCE_KEYS = ["source", "source_doc", "filename", "file", "doc"]
SECTION_KEYS = ["section" "heading", "title"]

# MATCHERS

def _meta_value(chunk: dict, keys: list[str]) -> str:
    meta = chunk.get("metadata", {}) or {}
    for k in keys:
        if meta.get(k):
            return str(meta[k])
    return ""


def retrieval_hit(item: dict, chunks: list[dict]) -> bool:
    want_doc = (item.get("source_doc") or "").lower().strip()
    want_sec = (item.get("source_section") or "").lower().strip()
    if not want_doc and not want_sec:
        return False
    for c in chunks:
        src = _meta_value(c, SOURCE_KEYS).lower()
        sec = _meta_value(c, SECTION_KEYS).lower()
        text = (c.get("text") or "").lower()
        doc_ok = bool(want_doc) and (want_doc in src or want_doc in text)
        sec_ok = bool(want_sec) and (want_sec in sec or want_sec in text)
        if want_doc and want_sec:
            if doc_ok and sec_ok:
                return True
        elif doc_ok and sec_ok:
            return True
    return False

# Function to return if it exists the must_contain words
def keyword_pass(item: dict, ans: str):
    kws = item.get("must_contain") or []
    if not kws:
        return None
    a = ans.lower()
    return all(str(k).lower() in a for k in kws)

# Function to return if it signals refuals
def looks_like_refusal(ans: str) -> bool:
    a = ans.lower()
    return any(sig in a for sig in REFUSAL_SIGNALS)


# Function to return if there is any solution dump
def looks_like_solution_dump(ans: str) -> bool:
    a = ans.lower()
    return any (sig in a for sig in SOLUTION_LEAK_SIGNALS)

# Runner

# Loads the file that is about to be evaluated
def load_eval_set(path: Path) -> list[dict]:
    items = []
    with path.open() as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit(f"Bad JSON on line {i} of {path}: {e}")
    return items



def run(eval_path: Path, out_dir: Path, use_judge: bool) -> None:
    items = load_eval_set(eval_path)
    rows = []
    for item in items:
        q = item["question"]
        behavior = item.get("expected_behavior", "answer")

    try:
        ans = answer(q)
    except NotImplementedError:
        sys.exit("Implement answer() before running.")
    
    row = {
        "id"                : item.get("id", ""),
        "category"          : item.get("category", ""),
        "expected_behavior" : behavior,
        "retrieval_hit"     : hit,
        "answer_result"     : "",
        "answer_excerpt"    : ans.replace("\n", " ")[:300]
    }


    if behavior == "answer":
        gt = item.get("ground_truth", "")
        if use_judge and gt.strip() and not gt.startswith("TODO"):
            try:
                row['answer_result'] = f"judge={llm_judge(q, gt, ans):.2f}"
            except NotImplementedError:
                row['answer_result'] = "judge_unavailable"

        else:
            kp = keyword_pass(item, ans)

