import sys
import os
import argparse
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
    parser = argparse.ArgumentParser(
            description="cozy-ssh local session state mapper",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("os",
            help="Evaluate if system is a particular platform",
            default="linux", choices=["linux", "windows", "win32", "win"])

    log = logging.getLogger("os_check")

    try:
        args = parser.parse_args()
    except SystemExit:
        log.error("[+] Failed to evaluate arguments")
        sys.exit(0)

    _os = "win32" if args.os in ["win", "win32", "windows"] else "linux"

    if sys.platform == _os:
        log.debug(f"[+] 👍 localhost os is {_os}")
        sys.exit(0)
    else:
        log.warning(f"[+] 🚫 localhost os is not {_os}")
        sys.exit(1)

if __name__ == "__main__":
    main()
