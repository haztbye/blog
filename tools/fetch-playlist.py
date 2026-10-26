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
import re
import sys
import time
import urllib.error
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


def fetch_lyrics(song_id, retries=1):
    """取 LRC 歌词（带时间轴）；纯音乐 / 无歌词 / 抓取失败返回空串"""
    for attempt in range(retries + 1):
        req = urllib.request.Request(LYRIC_API % song_id, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.load(resp)
            text = (data.get("lrc") or {}).get("lyric") or ""
            # 至少要有一行带时间轴，否则视为没有歌词
            if "[0" in text or "[1" in text:
                return text
            return ""
        except Exception:
            if attempt < retries:
                time.sleep(0.6)
    return ""


def playable(song_id, retries=2):
    """外链音频是否可播：True=确认可播，False=确认不可播，None=没问出来（网络/限流）

    注意：**只有拿到响应且确认不是音频时才返回 False**。请求异常一律返回 None，
    否则在 GitHub Runner 这种容易被限流的环境里会把好歌误删（真实踩过的坑）。
    """
    for attempt in range(retries + 1):
        req = urllib.request.Request(OUTER % song_id, headers=dict(HEADERS, Range="bytes=0-1024"))
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                ctype = (resp.headers.get("Content-Type") or "").lower()
                resp.read(64)
                return "audio" in ctype
        except urllib.error.HTTPError:
            # 有响应（例如 404 页面）→ 确认不可播
            return False
        except Exception:
            if attempt < retries:
                time.sleep(0.8)
    return None


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
    unknown = 0
    for track in tracks:
        if track.get("fee") == 1:  # VIP 专属：匿名播放器播不了
            skipped_vip += 1
            continue
        song_id = str(track.get("id", ""))
        if not song_id:
            continue
        # 实测外链音频：确认不可播才跳过；问不出来（限流/超时）先保留
        status = playable(song_id)
        if status is False:
            skipped_dead += 1
            print("[music] 跳过（外链确认不可播）：%s" % track.get("name", song_id))
            continue
        if status is None:
            unknown += 1
            print("[music] 无法确认（网络问题），先保留：%s" % track.get("name", song_id))
        artists = " / ".join(a.get("name", "") for a in (track.get("ar") or []) if a.get("name"))
        songs.append({
            "id": song_id,
            "name": track.get("name", ""),
            "artist": artists,
        })

    if not songs:
        print("[music] 歌单里没有真正可播的歌，保留现有文件")
        return 0

    # 安全阀：本次确认的曲目比上次少 → 保留旧文件，避免"限流导致歌曲凭空消失"
    previous_ids = []
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as fh:
                previous_ids = re.findall(r'^\s*-\s*id:\s*"?(\d+)"?', fh.read(), re.MULTILINE)
        except Exception:
            previous_ids = []

    write_playlist = True
    if previous_ids and len(songs) < len(previous_ids):
        write_playlist = False
        print("[music] 本次只确认 %d 首（上次 %d 首），保留旧歌单文件以免误删" % (len(songs), len(previous_ids)))

    if write_playlist:
        lines = [
            "# 本文件由 tools/fetch-playlist.py 自动生成，请勿手改",
            "# 歌单：%s（%s）" % (playlist.get("name", "?"), PLAYLIST_ID),
            "# 判定标准：fee != 1 且外链音频实测返回音频（确认不可播才剔除）",
            "",
        ]
        for song in songs:
            lines.append('- id: "%s"' % song["id"])
            lines.append("  name: %s" % json.dumps(song["name"], ensure_ascii=False))
            lines.append("  artist: %s" % json.dumps(song["artist"], ensure_ascii=False))

        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")

    # 歌词：单独放一个 JSON，页面播放时按需 fetch（不塞进 HTML，省首屏体积）
    # 与上一次的结果**合并**：某首抓失败就沿用旧歌词，绝不用残缺结果覆盖完整的
    previous = {}
    if os.path.exists(LYRICS_OUT):
        try:
            with open(LYRICS_OUT, encoding="utf-8") as fh:
                previous = json.load(fh) or {}
        except Exception:
            previous = {}

    lyrics = {}
    reused = 0
    for song in songs:
        text = fetch_lyrics(song["id"])
        if not text:
            text = previous.get(song["id"], "")
            if text:
                reused += 1
        if text:
            lyrics[song["id"]] = text
        time.sleep(0.3)   # 稍微错开，降低被限流的概率

    if len(lyrics) < len(previous):
        # 兜底：新结果比旧的还少，说明这次抓取不稳，保留旧文件
        print("[music] 本次只抓到 %d 首歌词（旧文件有 %d 首），保留旧歌词文件"
              % (len(lyrics), len(previous)))
    else:
        with open(LYRICS_OUT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(lyrics, ensure_ascii=False, separators=(",", ":")) + "\n")

    print("[music] 曲目 %d 首（跳过 VIP %d、确认失效 %d、无法确认保留 %d）-> %s%s"
          % (len(songs), skipped_vip, skipped_dead, unknown, OUT,
             "" if write_playlist else "（本次未覆盖）"))
    print("[music] 歌词 %d/%d 首（沿用旧歌词 %d 首）-> %s"
          % (len(lyrics), len(songs), reused, LYRICS_OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())