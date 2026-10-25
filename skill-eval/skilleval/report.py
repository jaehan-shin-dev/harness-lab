"""report.md, summary.csv (goal.md Q20). 평균은 '오염 의심'과 실패 회차를 뺀다 (goal.md R5 ④)."""
import csv
import datetime as dt
import json
import statistics
import subprocess
from pathlib import Path

from .config import PILAB
from .graders.process import CHECKS, LABELS
from .runner import END_LABELS


def skills_version() -> dict:
    def git(*a):
        return subprocess.run(["git", "-C", str(PILAB), *a], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL).stdout.strip()
    scope = [".agents/skills", "AGENTS.md"]
    return {"commit": git("log", "-1", "--format=%h", "--", *scope),
            "dirty": bool(git("status", "--porcelain", "--", *scope))}


def load_all(out_dir: Path) -> tuple[list, list]:
    scores, failed = [], []
    runs = out_dir / "runs"
    for d in sorted(runs.iterdir()) if runs.exists() else []:
        if not d.is_dir() or d.name.startswith("_"):
            continue
        meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        if (d / "scores.json").exists():
            s = json.loads((d / "scores.json").read_text())
            s["_meta"] = meta
            scores.append(s)
        elif (d / "failed.json").exists():
            failed.append({"run": d.name, "meta": meta, **json.loads((d / "failed.json").read_text())})
    return scores, failed


def ms(xs) -> str:
    xs = [x for x in xs if x is not None]
    if not xs:
        return "-"
    m = statistics.mean(xs)
    sd = statistics.stdev(xs) if len(xs) > 1 else 0.0
    return f"{m:.2f} ± {sd:.2f} (n={len(xs)})"


def judge_total(s):
    j = s.get("judge") or {}
    return j.get("rubric_total") if "rubric_total" in j else None


def judge_fact_rate(s):
    j = s.get("judge") or {}
    f = j.get("facts")
    return sum(v["captured"] for v in f.values()) / len(f) if f else None


def clean(s):
    return s["leak"]["status"] == "clean"


def cells(scores):
    out = {}
    for s in scores:
        out.setdefault((s["task"], s["arm"]), []).append(s)
    return out


def write_csv(scores, failed, path: Path):
    cols = ["run", "task", "arm", "rep", "end_reason", "rounds", "turns", "process_passed", *CHECKS,
            "recall_rate", "judge_rubric_total", "judge_fact_rate", "leak_status", "tok_input", "tok_output",
            "tok_cacheRead", "tok_cacheWrite", "tok_reasoning", "cost", "max_context_ratio", "tool_calls_total",
            "failed_calls", "compactions", "retries", "duration_s", "mock_cost"]
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for s in scores:
            t = s["trace"]["candidate"]
            w.writerow([s["run"], s["task"], s["arm"], s["rep"], s["end_reason"], s["rounds"], s["turns"],
                        s["process"]["passed"], *[int(s["process"]["checks"][c]["pass"]) for c in CHECKS],
                        s["recall"]["rate"], judge_total(s), judge_fact_rate(s), s["leak"]["status"],
                        *[t["tokens"][k] for k in ("input", "output", "cacheRead", "cacheWrite", "reasoning")],
                        t["cost"], t["max_context_ratio"], t["tool_calls_total"], t["failed_calls"],
                        t["compactions"], t["retries"], t["duration_s"], s["trace"]["mock_user"]["cost"]])
        for fl in failed:
            m = fl["meta"]
            w.writerow([fl["run"], m.get("task"), m.get("arm"), m.get("rep"), "failed"] + [""] * (len(cols) - 5))


def build_report(out_dir: Path, suite) -> Path:
    scores, failed = load_all(out_dir)
    metas = [s["_meta"] for s in scores] + [f["meta"] for f in failed]
    sv = skills_version()
    L = [f"# 보고서: {suite.name}", ""]
    L += ["## 머리말", "",
          f"- 작성: {dt.datetime.now().isoformat(timespec='seconds')}",
          f"- 모델: {sorted({m.get('provider', '?') + '/' + m.get('model', '?') for m in metas})}",
          f"- thinking: {metas[0].get('thinking') if metas else '-'}",
          f"- pi 버전: {sorted({m.get('pi_version', '?') for m in metas})}",
          f"- 스킬 버전: `.agents/skills`·AGENTS.md 마지막 커밋 {sv['commit']}"
          f"{', 커밋 안 된 변경 있음' if sv['dirty'] else ', 변경 없음'}",
          f"- 회차: 완료 {len(scores)}, 실패 {len(failed)}, 오염 의심 {sum(not clean(s) for s in scores)}",
          f"- 모의 사용자: {sorted({m.get('mock_policy', 'llm') for m in metas})}", ""]

    L += ["## 과제·팔별 요약", "",
          "평균 ± 표준편차. 오염 의심·실패 회차는 평균에서 뺀다. 과정은 8점 만점, 심판 루브릭은 10점 만점. "
          "과제 3(workflow-skill-fix)의 회수율·심판 사실 판정은 참고 값이다(한계 참고).", "",
          "| 과제 | 팔 | 회차(완료/깨끗) | 종료 사유 | 과정 | 회수율(키워드) | 심판 사실 판정 | 심판 루브릭 |",
          "|---|---|---|---|---|---|---|---|"]
    for (t, a), ss in sorted(cells(scores).items()):
        cs = [s for s in ss if clean(s)]
        ends = ", ".join(f"{END_LABELS[k]} {n}" for k in END_LABELS
                         if (n := sum(s["end_reason"] == k for s in ss)))
        L.append(f"| {t} | {a} | {len(ss)}/{len(cs)} | {ends} | {ms([s['process']['passed'] for s in cs])} | "
                 f"{ms([s['recall']['rate'] for s in cs])} | {ms([judge_fact_rate(s) for s in cs])} | "
                 f"{ms([judge_total(s) for s in cs])} |")
    L.append("")

    L += ["## 과정 검사 통과율", "", "| 검사 | " + " | ".join(f"{t}/{a}" for t, a in sorted(cells(scores))) + " |",
          "|---|" + "---|" * len(cells(scores))]
    for c in CHECKS:
        row = []
        for _, ss in sorted(cells(scores).items()):
            cs = [s for s in ss if clean(s)]
            row.append(f"{sum(s['process']['checks'][c]['pass'] for s in cs)}/{len(cs)}" if cs else "-")
        L.append(f"| {LABELS[c]} | " + " | ".join(row) + " |")
    L.append("")

    L += ["## 회차별", "",
          "| 회차 | 종료 | 라운드 | 과정 | 회수율 | 심판 루브릭 | 누출 검사 |", "|---|---|---|---|---|---|---|"]
    for s in scores:
        lk = "깨끗" if clean(s) else "오염 의심: " + "; ".join(s["leak"]["reasons"])[:300]
        if s["leak"].get("notes"):
            lk += f" (회차 폴더 안 읽기 {len(s['leak']['notes'])}회, 허용)"
        L.append(f"| {s['run']} | {END_LABELS.get(s['end_reason'], s['end_reason'])} | {s['rounds']} | "
                 f"{s['process']['passed']}/8 | {s['recall']['recalled']}/{s['recall']['total']} | "
                 f"{judge_total(s) if judge_total(s) is not None else '-'} | {lk} |")
    for fl in failed:
        L.append(f"| {fl['run']} | 실패 | - | - | - | - | 실패 사유: {fl['error'][:200]} |")
    L.append("")

    L += ["## 키워드와 심판이 다른 칸", "", "사람이 읽을 칸. 키워드 판정 Y/N, 심판 판정 Y/N.", "",
          "| 회차 | 사실 | 키워드 | 심판 | 심판 근거 |", "|---|---|---|---|---|"]
    nd = 0
    for s in scores:
        jf = (s.get("judge") or {}).get("facts") or {}
        for fid, kv in s["recall"]["facts"].items():
            if fid in jf and jf[fid]["captured"] != kv["recalled"]:
                nd += 1
                L.append(f"| {s['run']} | {fid} | {'Y' if kv['recalled'] else 'N'} {kv['hits'][:2]} | "
                         f"{'Y' if jf[fid]['captured'] else 'N'} | {jf[fid]['evidence'][:120]} |")
    if not nd:
        L.append("| (없음) | | | | |")
    jerr = [s["run"] for s in scores if (s.get("judge") or {}).get("error")]
    if jerr:
        L += ["", f"심판 호출 실패 회차: {jerr}"]
    L.append("")

    L += ["## 스킬 로드 확인 (C4)", "",
          "| 회차 | 1턴이 `<skill name=` | system skills 수 | project_context | 시험 대상 grill SKILL.md 읽음 | "
          "시험 대상 SKILL.md 읽기 | 작업 폴더 SKILL.md 읽기 | 끄기 옵션 |", "|---|---|---|---|---|---|---|---|"]
    for s in scores:
        k = s["trace"]["candidate"]["skill_load"]
        tested = s["trace"]["candidate"].get("tested_skill_md_read", [])
        flags = [f for f, on in (("--no-skills", k["cmd_no_skills"]), ("--no-context-files", k["cmd_no_context_files"]))
                 if on]
        L.append(f"| {s['run']} | {k['first_user_skill_name'] or '아니오'} | {k['sections_skills_count']} | "
                 f"{', '.join(Path(p).name for p in k['project_context_paths']) or '없음'} | "
                 f"{'예' if k['grill_skill_md_read'] else '아니오'} | {len(tested)} | "
                 f"{len(s['trace']['candidate']['skill_md_read']) - len(tested)} | "
                 f"{' '.join(flags) or '없음'} |")
    L.append("")

    L += ["## 실행 기록 평균 (점수에 쓰지 않음, goal.md R6)", "",
          "| 과제 | 팔 | 턴 | 라운드 | 입력 토큰 | 출력 토큰 | 캐시 읽기 | 추론 | 비용($) | 최대 컨텍스트 | 도구 호출 | 실패 호출 | "
          "압축 | 재시도 | 걸린 시간(초) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (t, a), ss in sorted(cells(scores).items()):
        tr = [s["trace"]["candidate"] for s in ss]
        avg = lambda xs: f"{statistics.mean(xs):.1f}" if xs else "-"
        L.append(f"| {t} | {a} | {avg([x['turns'] for x in tr])} | {avg([s['rounds'] for s in ss])} | "
                 f"{avg([x['tokens']['input'] for x in tr])} | {avg([x['tokens']['output'] for x in tr])} | "
                 f"{avg([x['tokens']['cacheRead'] for x in tr])} | {avg([x['tokens']['reasoning'] for x in tr])} | "
                 f"{statistics.mean([x['cost'] for x in tr]):.3f} | "
                 f"{statistics.mean([x['max_context_ratio'] or 0 for x in tr]):.1%} | "
                 f"{avg([x['tool_calls_total'] for x in tr])} | {avg([x['failed_calls'] for x in tr])} | "
                 f"{avg([x['compactions'] for x in tr])} | {avg([x['retries'] for x in tr])} | "
                 f"{avg([x['duration_s'] for x in tr])} |")
    L.append("")

    L += ["## 참고 기록 (점수 아님)", "",
          "| 회차 | 알려 준 사용자 사실 | 수락 결정 일치 | 찾을 수 있는 사실을 물음 | 모름 대답 | 모의 사용자 출력 보정 |",
          "|---|---|---|---|---|---|"]
    for s in scores:
        m = s.get("mock") or {}
        L.append(f"| {s['run']} | {', '.join(m.get('revealed', [])) or '-'} | {', '.join(m.get('accepted', [])) or '-'} | "
                 f"{m.get('findable_asked', 0)} | {m.get('unknown_items', 0)} | {len(m.get('fixes', []))} |")
    L.append("")

    L += ["## 한계", "",
          "- 심판은 후보와 같은 모델이다(goal.md C1). 자기 쪽에 후할 수 있다.",
          "- 스킬 팔의 goal.md([합의] 등)와 질문 글(❓, ➡️)에는 흔적이 있어 심판에게 팔이 완전히 가려지지 않는다.",
          "- 심판은 같은 입력에도 점수가 흔들린다(M1: 같은 goal.md 4회 호출에 루브릭 9~10점). 회차마다 1회만 부른다.",
          "- 심판 입력에는 후보 글과 모의 사용자 대답이 함께 들어간다(2026-10-22 결정). 첫 메시지는 팔이 드러나지 않게 과제의 시작 요청으로 바꾼다.",
          "- 공개 벤치마크(SWE-bench 이슈)는 모델이 외웠을 수 있다. 과제 3(workflow-skill-fix)은 비공개라 해당 없다.",
          "- 과제 3의 스킬 팔은 시험 대상 스킬 자체가 그 과제의 결과물(스킬 7개)이라, 스킬을 읽으면 끝 모양을 볼 수 있다. "
          "M2에서 실제로 로드된 스킬을 고칠 대상으로 보고 \"이미 됐다\"고 적었다. 그래서 과제 3의 회수율·심판 사실 판정은 "
          "참고로만 보고, 과정 검사는 그대로 쓴다(2026-10-23 결정).",
          "- 누출 검사는 회차 폴더 안(작업 폴더 + 설정 폴더) 읽기를 허용한다(2026-10-23 결정). 그 위·밖 경로와 쓰기는 오염 의심이다.",
          "- 모의 사용자 대답 문장은 답변표의 문장을 이어 붙여 만든다. 모델은 어떤 사실로 대답할지만 고른다.",
          "- 과제 3 작업 폴더의 옛 AGENTS.md는 스킬 팔에서 새 AGENTS.md와 함께 읽힌다(당시 조건). "
          f"이번 회차들: 작업 폴더 AGENTS.md 있음 {sum(bool(m.get('workspace_agents_md')) for m in metas)}회.",
          ""]
    out = out_dir / "report.md"
    out.write_text("\n".join(L))
    write_csv(scores, failed, out_dir / "summary.csv")
    return out
