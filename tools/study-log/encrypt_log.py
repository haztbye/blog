#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把考研日志的明文加密成 data/study-log.yaml —— 仓库里只有密文。

用法：
    python tools/study-log/encrypt_log.py [明文路径]

明文默认路径（**在仓库之外**，不会被 git 提交）：
    <repo 上级>/study-log-private/kaoyan-log.md

密码来源（优先级从高到低）：
    1. 环境变量 STUDY_LOG_KEY（仅测试用）
    2. 文件 %USERPROFILE%\\.huanhe-study-key（由 set-key.bat 生成）

加密方案：PBKDF2-HMAC-SHA256(210000 次) 派生 32 字节密钥 → AES-256-GCM
（带附加认证数据 b"huanhe-study-log"，与 static/js/study-log.js 保持一致）
"""

import base64
import datetime
import os
import re
import sys
from pathlib import Path

ITERATIONS = 210_000
AAD = b"huanhe-study-log"

ROOT = Path(__file__).resolve().parents[2]           # my-blog/
OUT = ROOT / "data" / "study-log.yaml"
JSON_OUT = ROOT / "static" / "study-log.json"
DEFAULT_SRC = ROOT.parent / "study-log-private" / "kaoyan-log.md"
KEY_FILE = Path(os.environ.get("USERPROFILE") or Path.home()) / ".huanhe-study-key"


def load_key():
    key = os.environ.get("STUDY_LOG_KEY")
    if key:
        return key.strip()
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8-sig").strip()
        if key:
            return key
    sys.exit(
        "[study-log] 没找到密码。请先运行 tools\\study-log\\set-key.bat 设置密码，"
        "或临时用 STUDY_LOG_KEY 环境变量。"
    )


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        os.environ.get("STUDY_LOG_SRC", str(DEFAULT_SRC))
    )
    if not src.exists():
        sys.exit("[study-log] 找不到明文文件：%s" % src)

    text = src.read_text(encoding="utf-8")
    if not text.strip():
        sys.exit("[study-log] 明文是空的，先写点东西再加密")

    key = load_key()
    if len(key) < 8:
        sys.exit("[study-log] 密码太短（至少 8 位），换一个再试")

    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    except ImportError:
        sys.exit("[study-log] 当前 Python 没有 cryptography 库，换个解释器再试")

    salt = os.urandom(16)
    iv = os.urandom(12)
    derived = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS
    ).derive(key.encode("utf-8"))
    ciphertext = AESGCM(derived).encrypt(iv, text.encode("utf-8"), AAD)

    b64 = lambda raw: base64.b64encode(raw).decode("ascii")  # noqa: E731
    entries = len(re.findall(r"^##\s", text, flags=re.MULTILINE)) or 1
    today = datetime.date.today().isoformat()

    lines = [
        "# 本文件由 tools/study-log/encrypt_log.py 自动生成，请勿手改",
        "# 里面只有密文；明文留在仓库外的 study-log-private/，密码只在你本机",
        "version: 1",
        "cipher: AES-256-GCM",
        "kdf: PBKDF2-SHA256",
        "iterations: %d" % ITERATIONS,
        'salt: "%s"' % b64(salt),
        'iv: "%s"' % b64(iv),
        'ct: "%s"' % b64(ciphertext),
        "entries: %d" % entries,
        'updated: "%s"' % today,
        "chars: %d" % len(text),
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    # 密文另存一份静态 JSON：页面用 fetch 读取，避开 Hugo 模板在 <script> 里的上下文转义
    import json as _json

    JSON_OUT.write_text(
        _json.dumps(
            {
                "version": 1,
                "cipher": "AES-256-GCM",
                "kdf": "PBKDF2-SHA256",
                "iterations": ITERATIONS,
                "salt": b64(salt),
                "iv": b64(iv),
                "ct": b64(ciphertext),
                "entries": entries,
                "updated": today,
                "chars": len(text),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print("[study-log] 已加密 %d 字符 / %d 篇 → %s" % (len(text), entries, OUT))
    print("[study-log] 密文 JSON → %s" % JSON_OUT)
    print("[study-log] 密码没有写入任何文件，仓库里只有密文")
    return 0


if __name__ == "__main__":
    sys.exit(main())