import sys
import os

def main():
    # If the OS is Linux, exit with 0 (True for Match exec)
    # If it is Windows ('nt'), exit with 1 (False for Match exec)
    if os.name != 'nt':
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    main()
