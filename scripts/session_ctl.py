"""cozy-ssh session lifecycle.

Write session_%C.conf, then hand off to a second ssh with ProxyCommand=none.

ProxyCommand only expands %% %h %n %p %r. %C and %j are derived here so the
filename matches OpenSSH (%C = SHA1 of %l%h%p%r%j).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import logging.config
import os
import shutil
import socket
import sys
import time
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


def conn_hash(local_host: str, hostname: str, port: str, user: str, jump: str) -> str:
    """Match OpenSSH %C: SHA1 of %l%h%p%r%j."""
    payload = f"{local_host}{hostname}{port}{user}{jump}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def session_path(hash_hex: str) -> Path:
    return CACHE_DIR / f"session_{hash_hex}.conf"


def write_session(
    original_target: str,
    resolved_target: str,
    hash_hex: str,
    init_host: str,
    jump: str,
) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = session_path(hash_hex)
    is_gateway = "0" if jump in ("", "none") else "1"
    body = (
        f'Match final host="{resolved_target}"\n'
        f"  SetEnv "
        f'__PROXYJUMP_GATE__="{is_gateway}" '
        f'__SSH_CONN_HASH_GATE__="{hash_hex}" '
        f'__SSH_CONN_INIT_HOST_GATE__="{init_host}" '
        f'__SSH_ORIGINAL_TARGET_GATE__="{original_target}" '
        f'__SSH_RESOLVED_TARGET_GATE__="{resolved_target}" '
        f'__SSH_PROXYJUMP_GATE__="{jump or "none"}"\n'
    )
    path.write_text(body, encoding="utf-8")
    log.debug("[+] wrote %s", path)
    return path


def find_ssh() -> str:
    found = shutil.which("ssh")
    if not found:
        log.error("ssh not on PATH")
        sys.exit(1)
    return found


def cmd_proxy(args: argparse.Namespace) -> None:
    jump = args.jump or ""
    if jump.lower() in ("none", "none"):
        jump = ""
    local_l = socket.getfqdn()
    local_L = socket.gethostname().split(".")[0]
    port = str(args.port or "22")
    user = args.user or os.environ.get("USERNAME") or os.environ.get("USER") or ""
    hex_c = conn_hash(local_l, args.host, port, user, jump)
    write_session(
        original_target=args.original,
        resolved_target=args.host,
        hash_hex=hex_c,
        init_host=local_L,
        jump=jump,
    )

    ssh = find_ssh()
    dest = args.host
    inner = [
        ssh,
        "-o",
        "ProxyCommand=none",
        dest,
    ]
    if args.user:
        inner[1:1] = ["-l", args.user]
    log.debug("[+] exec %s", " ".join(inner))
    os.execvp(ssh, inner)


def cmd_init(args: argparse.Namespace) -> None:
    jump = args.jump or ""
    if jump.lower() == "none":
        jump = ""
    local_l = socket.getfqdn()
    local_L = socket.gethostname().split(".")[0]
    port = str(args.port or "22")
    user = args.user or os.environ.get("USERNAME") or os.environ.get("USER") or ""
    host = args.target
    hex_c = conn_hash(local_l, host, port, user, jump)
    path = write_session(host, host, hex_c, local_L, jump)
    log.info("[+] init %s -> %s", host, path.name)


def cmd_kill(args: argparse.Namespace) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    if args.hash:
        path = session_path(args.hash)
        if path.exists():
            path.unlink()
            removed += 1
            log.info("[+] removed %s", path.name)
    elif args.target:
        needle = args.target.lower()
        for path in CACHE_DIR.glob("session_*.conf"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if needle in text.lower():
                path.unlink()
                removed += 1
                log.info("[+] removed %s", path.name)
    else:
        log.error("kill needs --hash or a target")
        sys.exit(2)
    log.info("[+] kill removed %s file(s)", removed)


def cmd_reinit(args: argparse.Namespace) -> None:
    cmd_kill(args)
    cmd_init(args)


def cmd_clean(args: argparse.Namespace) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - (args.minutes * 60)
    removed = 0
    for path in CACHE_DIR.glob("session_*.conf"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
                log.info("[+] cleaned %s", path.name)
        except OSError as e:
            log.error("%s: %s", path, e)
    log.info("[+] clean removed %s file(s)", removed)


def cmd_connect(args: argparse.Namespace) -> None:
    cmd_init(args)
    ssh = find_ssh()
    inner = [ssh, "-o", "ProxyCommand=none", args.target]
    if args.port:
        inner.extend(["-p", str(args.port)])
    if args.user:
        inner.extend(["-l", args.user])
    if args.jump and args.jump.lower() != "none":
        inner.extend(["-J", args.jump])
    inner.extend(args.ssh_args)
    log.debug("[+] exec %s", " ".join(inner))
    os.execvp(ssh, inner)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="cozy-ssh session control")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("proxy", help="ProxyCommand entry: write session file, then ssh -W")
    p.add_argument("original", help="%%n")
    p.add_argument("host", help="%%h")
    p.add_argument("port", help="%%p")
    p.add_argument("user", nargs="?", default="", help="%%r")
    p.add_argument("--jump", default="", help="ProxyJump host if known")
    p.set_defaults(func=cmd_proxy)

    p = sub.add_parser("init", help="Write session file only")
    p.add_argument("target")
    p.add_argument("--jump", default="")
    p.add_argument("--port", default="22")
    p.add_argument("--user", default="")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("kill", help="Delete session file(s)")
    p.add_argument("target", nargs="?")
    p.add_argument("--hash", default="")
    p.add_argument("--jump", default="")
    p.add_argument("--port", default="22")
    p.add_argument("--user", default="")
    p.set_defaults(func=cmd_kill)

    p = sub.add_parser("reinit", help="kill then init")
    p.add_argument("target")
    p.add_argument("--hash", default="")
    p.add_argument("--jump", default="")
    p.add_argument("--port", default="22")
    p.add_argument("--user", default="")
    p.set_defaults(func=cmd_reinit)

    p = sub.add_parser("clean", help="Delete session files older than N minutes")
    p.add_argument("--minutes", type=int, default=60)
    p.set_defaults(func=cmd_clean)

    p = sub.add_parser("connect", help="init, then exec ssh with ProxyCommand=none")
    p.add_argument("target")
    p.add_argument("--jump", default="")
    p.add_argument("--port", default="22")
    p.add_argument("--user", default="")
    p.add_argument("ssh_args", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_connect)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
