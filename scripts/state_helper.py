import os
import sys
import argparse
from pathlib import Path
import json

try:
  import logging.config
  script_dir = os.path.dirname(os.path.abspath(__file__))
  with open(f'{script_dir}/log_config.json', 'r', encoding="utf-8") as f:
      log_conf = json.load(f)
  logging.config.dictConfig(log_conf)
except Exception as e:
    import logging
    log = logging.getLogger(__name__)
    log.error(getattr(e, '__dict__', str(e)))

def main():
    log = logging.getLogger("cozy_ssh")
    parser = argparse.ArgumentParser(
        description="cozy-ssh local session state mapper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("original_target", help="Original input text passed to SSH (%%n)")
    parser.add_argument("resolved_target", help="Resolved target hostname or IP (%%h)")
    parser.add_argument("conn_hash", help="Unique connection identifier hash (%%C)")
    parser.add_argument("init_host", help="Local workstation hostname executing the command (%%L)")
    parser.add_argument("proxy_jump_content", help="ProxyJump Content (%%j)") 

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(0)

    is_gateway = "0" if args.proxy_jump_content in ("", "none") else "1"


    cache_dir = Path.home() / ".ssh" / "cache"
    cache_dir.mkdir(exist_ok=True)
    session_file = cache_dir / f"session_{args.conn_hash}.conf"

    log.debug("[+] Mapping local session state")
    log.debug(f" -> Target input: {args.original_target}")
    log.debug(f" -> Target routed: {args.resolved_target}")
    log.debug(f" -> Gateway mode: {is_gateway}")
    log.debug(f" -> Initiating host: {args.init_host}")
    log.debug(f" -> ProxyJump: {args.proxy_jump_content or 'none'}")

    try:
        with open(session_file, "w") as f:
            f.write(f'Match final host="{args.resolved_target}"\n')
            f.write(
                f'  SetEnv '
                f'__PROXYJUMP_GATE__="{is_gateway}" '
                f'__SSH_CONN_HASH_GATE__="{args.conn_hash}" '
                f'__SSH_CONN_INIT_HOST_GATE__="{args.init_host}" '
                f'__SSH_ORIGINAL_TARGET_GATE__="{args.original_target}" '
                f'__SSH_RESOLVED_TARGET_GATE__="{args.resolved_target}"\n'
            )
            log.debug(f" -> Conf file: {session_file}")
    except Exception as e:
        log.error(getattr(e, '__dict__', str(e)))


if __name__ == "__main__":

  main()
