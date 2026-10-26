#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把图片加密后放进 static/study-log-media/（只有用密码在浏览器里解密才看得到）

用法：
    python tools/study-log/encrypt_media.py <图片路径> <名字>

- 图片先转成 WebP（最长边 1600px）并丢掉 EXIF，再加密
- 密钥与日志正文相同（同一份 salt/迭代次数），浏览器解锁后可直接复用派生密钥
- 密文写入 static/study-log-media/<名字>.bin，索引写入同目录 index.json
- 正文里用 ![](media:<名字>) 引用；encrypt_log.py 会把索引并进密文 JSON
"""

import base64
import io
import json
import os
import sys
from pathlib import Path

AAD = b"huanhe-study-log-media"
MAX_W = 1600
QUALITY = 82

ROOT = Path(__file__).resolve().parents[2]           # my-blog/
MEDIA_DIR = ROOT / "static" / "study-log-media"
INDEX = MEDIA_DIR / "index.json"
HOME = Path(os.environ.get("USERPROFILE") or Path.home())
KEY_FILE = HOME / ".huanhe-study-key"
SALT_FILE = HOME / ".huanhe-study-salt"      # 与 encrypt_log.py 共用同一份固定 salt


def load_key():
    key = os.environ.get("STUDY_LOG_KEY")
    if key:
        return key.strip()
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8-sig").strip()
        if key:
            return key
    sys.exit("[media] 没找到密码：先运行 set-key.bat")


def main():
    if len(sys.argv) < 3:
        sys.exit("用法: encrypt_media.py <图片路径> <名字>")
    src = Path(sys.argv[1])
    name = sys.argv[2].strip()
    if not src.exists():
        sys.exit("[media] 找不到图片：%s" % src)
    if not name or "/" in name or "\\" in name:
        sys.exit("[media] 名字不合法（别带路径分隔符）")

    from PIL import Image

    img = Image.open(src)
    img = img.convert("RGB")
    if img.width > MAX_W:
        img = img.resize((MAX_W, round(img.height * MAX_W / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=QUALITY, method=6)
    raw = buf.getvalue()

    # 复用日志正文的固定 salt / 迭代次数，浏览器解锁时派生出的密钥可以直接用
    if not SALT_FILE.exists():
        sys.exit("[media] 还没有 salt 文件：先跑一次 publish-log.bat（加密正文）再试")
    salt = base64.b64decode(SALT_FILE.read_text(encoding="utf-8").strip())
    iterations = 210_000

    key = load_key()
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    except ImportError:
        sys.exit("[media] 当前 Python 没有 cryptography，换个解释器再试")

    derived = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations
    ).derive(key.encode("utf-8"))

    iv = os.urandom(12)
    ciphertext = AESGCM(derived).encrypt(iv, raw, AAD)

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    blob = MEDIA_DIR / ("%s.bin" % name)
    blob.write_bytes(ciphertext)

    index = {}
    if INDEX.exists():
        try:
            index = json.loads(INDEX.read_text(encoding="utf-8"))
        except Exception:
            index = {}
    index[name] = {
        "file": blob.name,
        "iv": base64.b64encode(iv).decode("ascii"),
        "type": "image/webp",
        "width": img.width,
        "height": img.height,
        "bytes": len(raw),
    }
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")

    print("[media] %s -> %s（原图 %.0fKB → WebP %.0fKB → 密文 %.0fKB，%dx%d）" % (
        src.name[:36], blob.name, len(src.read_bytes()) / 1024, len(raw) / 1024,
        len(ciphertext) / 1024, img.width, img.height))
    print("[media] 正文里写 ![](media:%s) 即可引用" % name)
    return 0


if __name__ == "__main__":
    sys.exit(main())