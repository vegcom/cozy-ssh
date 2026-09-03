"""Write ~/.ssh/cache/session_%C.conf for Include on this ssh parse.

OpenSSH tokens, in order: %n %h %C %L %j.
Always exits 0 so Match exec stays a side effect.
"""

from __future__ import annotations

import json
import logging
import logging.config
import os
import sys
from pathlib import Path

try:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{_script_dir}/log_config.json", "r", encoding="utf-8") as _f:
        logging.config.dictConfig(json.load(_f))
except Exception as e:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("cozy_ssh").error(getattr(e, "__dict__", str(e)))

log = logging.getLogger("cozy_ssh")

CACHE_DIR = Path.home() / ".ssh" / "cache"


def main() -> None:
    if len(sys.argv) != 6:
        log.error("usage: session_ctl.py %%n %%h %%C %%L %%j")
        sys.exit(0)

    original, resolved, conn_hash, init_host, jump = sys.argv[1:6]

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"session_{conn_hash}.conf"

    try:
        body = (
            f'Match final host="{resolved}"\n'
            f"  SetEnv "
            f'__SSH_CONN_HASH_GATE__="{conn_hash}" '
            f'__SSH_CONN_INIT_HOST_GATE__="{init_host}" '
            f'__SSH_ORIGINAL_TARGET_GATE__="{original}" '
            f'__SSH_PROXYJUMP_GATE__="{jump}" '
            f'__SSH_RESOLVED_TARGET_GATE__="{resolved}"\n'
        )
        old = path.read_text(encoding="utf-8") if path.exists() else None

        if old is None:
            log.info("[+] creating %s", path.name)
            path.write_text(body, encoding="utf-8")
        elif old != body:
            log.info("[+] replacing %s", path.name)
            path.write_text(body, encoding="utf-8")
        else:
            log.info("[+] using cached %s", path.name)

    except Exception as e:
        log.error("%s: %s", path, e)

    sys.exit(0)


if __name__ == "__main__":
    main()