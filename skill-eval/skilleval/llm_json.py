"""pi로 순수 텍스트 모델을 불러 JSON 하나를 받는다 (모의 사용자·심판 공통)."""
import json
import re

from .events import assistant_text, messages, parse_jsonl
from .pi_process import run_pi


def extract_json(text: str):
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < i:
        raise ValueError("JSON 없음")
    return json.loads(t[i:j + 1])


def call_json(cfg, *, system_prompt: str, message: str, thinking: str, timeout: float, cwd, agent_dir,
              prompt_dir, log, label: str, tries: int = 2):
    """시스템 프롬프트는 파일로 넘긴다(ps에 답변 내용이 안 보이게). log(record)로 원본을 남긴다."""
    sp = prompt_dir / "system.md"
    last_err = None
    for attempt in range(1, tries + 1):
        sp.write_text(system_prompt)
        cmd = ["pi", "-p", "--mode", "json", "--provider", cfg.provider, "--model", cfg.model,
               "--thinking", thinking, "--no-tools", "--no-session", "--no-skills", "--no-context-files",
               "--no-extensions", "--no-mcp", "--no-approve", "--no-prompt-templates",
               "--system-prompt", str(sp), "--", message]
        try:
            r = run_pi(cmd, cwd, agent_dir, timeout)
        finally:
            sp.unlink(missing_ok=True)
        events = parse_jsonl(r["stdout"])
        log({"_runner": "call_start", "label": label, "attempt": attempt, "cmd": cmd[:-1] + ["<message>"],
             "prompt": message})
        for e in events:
            log(e)
        text = assistant_text(events)
        err = None
        if r["timed_out"]:
            err = "시간 초과"
        elif r["returncode"] != 0:
            err = f"종료 코드 {r['returncode']}: {r['stderr'][-300:]}"
        else:
            try:
                data = extract_json(text)
                log({"_runner": "call_end", "label": label, "attempt": attempt, "ok": True,
                     "duration_s": r["duration_s"]})
                return data, {"attempts": attempt, "duration_s": r["duration_s"],
                              "usage": [m.get("usage") for m in messages(events, "assistant")]}
            except (ValueError, json.JSONDecodeError) as ex:
                err = f"JSON 파싱 실패: {ex}"
        last_err = err
        log({"_runner": "call_end", "label": label, "attempt": attempt, "ok": False, "error": err,
             "stderr": r["stderr"][-1000:]})
    raise RuntimeError(f"{label}: {last_err}")
