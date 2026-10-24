#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取网易云公开歌单，生成 data/music.yaml（播放器用）

- 只保留可免费播放的曲目（fee=1 的 VIP 歌曲在未登录状态下播不了，直接跳过）
- 抓取失败时保留旧文件并正常退出，绝不让部署挂掉
- 歌单 ID 可用环境变量 NETEASE_PLAYLIST_ID 覆盖，默认见下方
"""

import json
import os
import sys
import urllib.request

PLAYLIST_ID = os.environ.get("NETEASE_PLAYLIST_ID", "2713947365")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "music.yaml")
API = "https://music.163.com/api/v6/playlist/detail?id=%s&n=1000"


def main():
    req = urllib.request.Request(
        API % PLAYLIST_ID,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://music.163.com/",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.load(resp)
    except Exception as exc:  # 网络/接口问题：保留旧数据
        print("[music] 抓取失败，保留现有 data/music.yaml：%s" % exc)
        return 0

    playlist = data.get("playlist") or {}
    tracks = playlist.get("tracks") or []
    if data.get("code") != 200 or not tracks:
        print("[music] 歌单不可用（code=%s，可能被设为私密），保留现有文件" % data.get("code"))
        return 0

    songs = []
    skipped_vip = 0
    for track in tracks:
        if track.get("fee") == 1:  # VIP 专属：匿名播放器播不了
            skipped_vip += 1
            continue
        artists = " / ".join(a.get("name", "") for a in (track.get("ar") or []) if a.get("name"))
        songs.append({
            "id": str(track.get("id", "")),
            "name": track.get("name", ""),
            "artist": artists,
        })

    if not songs:
        print("[music] 歌单里没有可免费播放的歌，保留现有文件")
        return 0

    lines = [
        "# 本文件由 tools/fetch-playlist.py 自动生成，请勿手改",
        "# 歌单：%s（%s）" % (playlist.get("name", "?"), PLAYLIST_ID),
        "",
    ]
    for song in songs:
        lines.append('- id: "%s"' % song["id"])
        lines.append("  name: %s" % json.dumps(song["name"], ensure_ascii=False))
        lines.append("  artist: %s" % json.dumps(song["artist"], ensure_ascii=False))

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print("[music] 写入 %d 首可播放曲目（跳过 VIP %d 首）-> %s" % (len(songs), skipped_vip, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())