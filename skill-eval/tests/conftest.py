import json
import time
from dataclasses import replace
from pathlib import Path

import pytest

from skilleval.config import load_config
from skilleval.suite import load_suite

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def fake_auth(tmp_path):
    p = tmp_path / "auth.json"
    p.write_text(json.dumps({"openai-codex": {"type": "oauth", "access": "a", "refresh": "real-refresh",
                                              "expires": int((time.time() + 100 * 3600) * 1000), "accountId": "x"}}))
    return p


@pytest.fixture
def cfg(fake_auth):
    c = load_config()
    return replace(c, auth={**c.auth, "source": str(fake_auth)}, retries={"pi_call": 0, "json_parse": 1})


@pytest.fixture
def suite():
    return load_suite("workflow-define")


@pytest.fixture
def task3(suite):
    return suite.task("workflow-skill-fix")
