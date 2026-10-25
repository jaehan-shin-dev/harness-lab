"""pi 프로세스 한 번 부르기 (후보·모의 사용자·심판 공통)."""
import os
import signal
import subprocess
import time

from .config import PILAB

# pi에 넘기는 환경 변수는 이것만. 나머지(PWD·OLDPWD·VIRTUAL_ENV, 이 도구를 띄운 세션의 값)는
# 이 도구의 위치나 다른 세션의 토큰을 후보에게 알려 준다(M2: PATH의 .venv로 skill-eval 경로가 보임)
KEEP_ENV = ("HOME", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL", "LC_CTYPE", "TERM", "TMPDIR", "TZ",
            "__CF_USER_TEXT_ENCODING", "http_proxy", "https_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY",
            "NO_PROXY", "SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS")


def clean_env(agent_dir) -> dict:
    env = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    env["PATH"] = os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep)
                                  if p and not p.startswith(str(PILAB)) and ".venv" not in p)
    env.update(PI_CODING_AGENT_DIR=str(agent_dir), PI_OFFLINE="1")
    return env


def run_pi(cmd: list, cwd, agent_dir, timeout: float) -> dict:
    """stdin은 닫는다(안 닫으면 pi가 끝없이 기다림, research/pi-smoke.md). 시간 초과 시 프로세스 묶음을 죽인다."""
    env = clean_env(agent_dir)
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout)   # 두 파이프를 끝까지 계속 읽는다(멈춤 방지)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    return {"returncode": proc.returncode, "stdout": out, "stderr": err.decode("utf-8", "replace"),
            "duration_s": round(time.monotonic() - t0, 2), "timed_out": timed_out, "pid": proc.pid}


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
