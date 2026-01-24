import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Configurable paths
home = Path.home()
key_dir = home / ".ssh" / "keys"
archive_dir = key_dir.parent / "keys-archive"
archive_dir.mkdir(parents=True, exist_ok=True)

key_types = ["rsa", "ecdsa", "ed25519"]
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

print("🔁 Rotating SSH keys...")

for key_type in key_types:
    key = key_dir / f"id_{key_type}"
    pub = key.with_name(f"{key.name}.pub")
    new_key = key_dir / f"id_{key_type}.new"
    new_pub = new_key.with_name(f"{new_key.name}.pub")

    # Backup to .bak
    if key.exists():
        print(f"📦 Creating .bak for {key_type}...")
        shutil.copy2(key, key_dir / f"id_{key_type}.bak")
        if pub.exists():
            shutil.copy2(pub, key_dir / f"id_{key_type}.bak.pub")

    # Archive with timestamp
    if key.exists():
        print(f"🗃️ Archiving {key_type} key...")
        shutil.copy2(key, archive_dir / f"id_{key_type}.{timestamp}")
        if pub.exists():
            shutil.copy2(pub, archive_dir / f"id_{key_type}.pub.{timestamp}")

    # Generate new key
    print(f"🔐 Generating new {key_type} key...")
    subprocess.run([
        "ssh-keygen", "-t", key_type,
        "-f", str(new_key),
        "-C", ""
        "-N", ""
    ], check=True,
    stdin=subprocess.DEVNULL
    )

    # Replace old key with new
    shutil.move(str(new_key), key)
    if new_pub.exists():
        shutil.move(str(new_pub), pub)
    else:
        print(f"⚠️ Public key not found: {new_pub}")

    # Append new public key to authorized_keys (idempotent)
    authorized_keys = key_dir.parent / "authorized_keys"
    authorized_keys.touch(mode=0o600, exist_ok=True)

    if pub.exists():
        new_key_text = pub.read_text().strip()

        if new_key_text not in authorized_keys.read_text():
            with authorized_keys.open("a") as ak:
                ak.write(new_key_text + "\n")
            print(f"🔑 Added {pub.name} to authorized_keys")
        else:
            print(f"ℹ️ {pub.name} already present in authorized_keys")

    # Set permissions
    try:
        os.chmod(key, 0o600)
        os.chmod(pub, 0o644)
    except Exception:
        pass

print("✅ Rotation complete.")
