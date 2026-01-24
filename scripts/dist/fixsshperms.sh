#!/bin/bash

set -euo pipefail

SSH_DIR="$HOME/.ssh"

find "$SSH_DIR" -type d -exec chmod 700 {} \;

find "$SSH_DIR" -type f -name "id_*" ! -name "*.pub" -exec chmod 600 {} \;
find "$SSH_DIR/keys" -type f -name "*.pub" -exec chmod 600 {} \;
find "$SSH_DIR" -type f -name "config" -exec chmod 600 {} \;
find "$SSH_DIR" -type f -name "authorized_keys" -exec chmod 600 {} \;

if [ -d "$SSH_DIR/ssh_config.d" ]; then
    find "$SSH_DIR/ssh_config.d" -type f -exec chmod 600 {} \;
fi

if [ -d "$SSH_DIR/known_hosts" ]; then
    find "$SSH_DIR/known_hosts" -type f -exec chmod 600 {} \;
fi

find "$SSH_DIR" -type f -name "*.pub" -exec chmod 644 {} \;

find "$SSH_DIR" -type f \
    ! -name "*.pub" \
    ! -name "id_*" \
    ! -name "config" \
    ! -name "authorized_keys" \
    ! -path "$SSH_DIR/ssh_config.d/*" \
    ! -path "$SSH_DIR/known_hosts/*" \
    -exec chmod 600 {} \;