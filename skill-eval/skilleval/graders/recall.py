"""답변표 회수율: 사용자 사실(Plan Q36)만, 키워드 패턴 하나라도 맞으면 회수 (goal.md R2)."""
import re


def fact_hits(fact, text: str) -> list:
    return [k for k in fact.keywords if re.search(k, text or "", re.I | re.M)]


def run_recall(answer, goal_text: str | None) -> dict:
    facts = [f for f in answer.facts if f.scored]
    per = {}
    for f in facts:
        hits = fact_hits(f, goal_text or "")
        per[f.id] = {"recalled": bool(hits), "hits": hits}
    n = sum(v["recalled"] for v in per.values())
    return {"recalled": n, "total": len(facts), "rate": round(n / len(facts), 4) if facts else None, "facts": per}
