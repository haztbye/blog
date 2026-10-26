#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取网易云公开歌单，生成 data/music.yaml + static/music-lyrics.json（播放器用）

- 只保留**真的能匿名播放**的曲目：先跳过 fee=1 的 VIP，再实测外链音频地址
  （VIP / 下架的歌会跳到 404 页面）
- 顺手抓每个曲目的 LRC 歌词（带时间轴），写进 static/music-lyrics.json 供右侧歌词栏用
- 抓取失败时保留旧文件并正常退出，绝不让部署挂掉
- 歌单 ID 可用环境变量 NETEASE_PLAYLIST_ID 覆盖，默认见下方
"""

import json
import os
import sys
import urllib.request

PLAYLIST_ID = os.environ.get("NETEASE_PLAYLIST_ID", "18521514782")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "music.yaml")
LYRICS_OUT = os.path.join(ROOT, "static", "music-lyrics.json")
API = "https://music.163.com/api/v6/playlist/detail?id=%s&n=1000"
OUTER = "https://music.163.com/song/media/outer/url?id=%s.mp3"
LYRIC_API = "https://music.163.com/api/song/lyric?id=%s&lv=1&kv=1&tv=-1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://music.163.com/",
}


def fetch_lyrics(song_id):
    """取 LRC 歌词（带时间轴）；纯音乐 / 无歌词返回空串"""
    req = urllib.request.Request(LYRIC_API % song_id, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except Exception:
        return ""
    text = (data.get("lrc") or {}).get("lyric") or ""
    # 至少要有一行带时间轴，否则视为没有歌词
    return text if ("[0" in text or "[1" in text) else ""


def playable(song_id):
    """外链音频地址是否真的返回音频（而不是 404 页面）"""
    req = urllib.request.Request(OUTER % song_id, headers=dict(HEADERS, Range="bytes=0-1024"))
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            resp.read(64)
            return "audio" in ctype
    except Exception:
        return False


def main():
    req = urllib.request.Request(API % PLAYLIST_ID, headers=HEADERS)
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
    skipped_dead = 0
    for track in tracks:
        if track.get("fee") == 1:  # VIP 专属：匿名播放器播不了
            skipped_vip += 1
            continue
        song_id = str(track.get("id", ""))
        if not song_id:
            continue
        # 实测外链音频：确认真的能播（VIP / 下架 / 版权受限的会跳到 404 页面）
        if not playable(song_id):
            skipped_dead += 1
            print("[music] 跳过（外链不可播）：%s" % track.get("name", song_id))
            continue
        artists = " / ".join(a.get("name", "") for a in (track.get("ar") or []) if a.get("name"))
        songs.append({
            "id": song_id,
            "name": track.get("name", ""),
            "artist": artists,
        })

    if not songs:
        print("[music] 歌单里没有真正可播的歌，保留现有文件")
        return 0

    lines = [
        "# 本文件由 tools/fetch-playlist.py 自动生成，请勿手改",
        "# 歌单：%s（%s）" % (playlist.get("name", "?"), PLAYLIST_ID),
        "# 判定标准：fee != 1 且外链音频地址实测返回音频",
        "",
    ]
    for song in songs:
        lines.append('- id: "%s"' % song["id"])
        lines.append("  name: %s" % json.dumps(song["name"], ensure_ascii=False))
        lines.append("  artist: %s" % json.dumps(song["artist"], ensure_ascii=False))

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    # 歌词：单独放一个 JSON，页面播放时按需 fetch（不塞进 HTML，省首屏体积）
    lyrics = {}
    for song in songs:
        text = fetch_lyrics(song["id"])
        if text:
            lyrics[song["id"]] = text
    with open(LYRICS_OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(lyrics, ensure_ascii=False, separators=(",", ":")) + "\n")

    print("[music] 写入 %d 首可播放曲目（跳过 VIP %d 首、外链失效 %d 首）-> %s"
          % (len(songs), skipped_vip, skipped_dead, OUT))
    print("[music] 歌词 %d/%d 首 -> %s" % (len(lyrics), len(songs), LYRICS_OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())