#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""密码自检：确认「你记得的密码」能不能解开当前密文。

用法：
    python tools/study-log/verify_key.py           # 检查本机密码文件（.huanhe-study-key）
    python tools/study-log/verify_key.py --ask     # 手动输入一次密码来检查（输入不显示）

只输出成功/失败与字数，不会打印密码或日志内容。
"""

import base64
import getpass
import json
import os
import sys
from pathlib import Path

AAD = b"huanhe-study-log"
ROOT = Path(__file__).resolve().parents[2]
JSON_FILE = ROOT / "static" / "study-log.json"
KEY_FILE = Path(os.environ.get("USERPROFILE") or Path.home()) / ".huanhe-study-key"


def try_decrypt(password):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    if not JSON_FILE.exists():
        sys.exit("[verify] 还没有密文（%s），先运行 publish-log.bat" % JSON_FILE)

    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    derived = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.b64decode(data["salt"]),
        iterations=data["iterations"],
    ).derive(password.encode("utf-8"))
    try:
        plain = AESGCM(derived).decrypt(
            base64.b64decode(data["iv"]), base64.b64decode(data["ct"]), AAD
        )
        return plain.decode("utf-8")
    except Exception:
        return None


def main():
    ask = "--ask" in sys.argv
    if ask:
        password = getpass.getpass("输入你想验证的密码（不显示）: ")
        source = "手动输入"
    else:
        if not KEY_FILE.exists():
            sys.exit("[verify] 本机没有密码文件：先运行 set-key.bat")
        password = KEY_FILE.read_text(encoding="utf-8-sig").strip()
        source = "本机密码文件"

    if not password:
        sys.exit("[verify] 密码是空的")

    plain = try_decrypt(password)
    if plain is None:
        print("[verify] ✗ 这个密码解不开当前密文（来源：%s）" % source)
        print("         可能：密码记错了 / 密文是另一个密码加密的（重新 set-key.bat 后跑一次 publish-log.bat）")
        return 1

    h2 = plain.count("\n## ")
    print("[verify] ✓ 密码可用（来源：%s）" % source)
    print("         解出 %d 字符，约 %d 篇记录" % (len(plain), h2 + (0 if plain.startswith("#") else 0)))
    print("         密码长度 %d 位（内容不会显示在这里）" % len(password))
    return 0


if __name__ == "__main__":
    sys.exit(main())