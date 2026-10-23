<?php
/**
 * 极简 Meting 风格接口：网易云歌单 -> APlayer 音频列表
 *
 * 用法：/meting/api.php?type=playlist&id=<网易云歌单ID>&limit=200
 *
 * 返回：
 *   成功：{ name, cover, url, trackCount, tracks: [{ id, name, artist, url, cover, vip }, ...] }
 *   失败：{ error: "...", detail: "..." }   （HTTP 仍是 200，便于前端统一处理）
 *
 * 说明：
 *  - 音频地址使用网易云官方外链接口（/song/media/outer/url），浏览器直接拉流，
 *    不经过本站服务器，因此不消耗本站带宽。
 *  - 结果缓存 10 分钟，减少对网易云的请求。
 *  - VIP 歌曲（fee=1）没有会员身份时无法播放，因此带 vip 标记返回，
 *    前端只把可播放的曲目交给播放器，VIP 曲目单独列出并提供网易云链接。
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: public, max-age=600');

$type  = isset($_GET['type']) ? (string) $_GET['type'] : 'playlist';
$id    = isset($_GET['id']) ? preg_replace('/\D/', '', (string) $_GET['id']) : '';
$limit = isset($_GET['limit']) ? max(1, min(1000, (int) $_GET['limit'])) : 200;

if ($type !== 'playlist' || $id === '') {
    echo json_encode(['error' => 'usage: ?type=playlist&id=PLAYLIST_ID'], JSON_UNESCAPED_UNICODE);
    exit;
}

$cacheDir  = __DIR__ . '/cache';
$cacheFile = $cacheDir . '/netease_playlist_' . $id . '_' . $limit . '.json';

if (is_file($cacheFile) && (time() - (int) filemtime($cacheFile)) < 600) {
    readfile($cacheFile);
    exit;
}

$apiUrl = 'https://music.163.com/api/v6/playlist/detail?id=' . $id . '&n=1000';
$ch = curl_init($apiUrl);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 15,
    CURLOPT_HTTPHEADER     => [
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer: https://music.163.com/',
    ],
]);
$raw = curl_exec($ch);
$httpCode = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
curl_close($ch);

if ($raw === false || $httpCode !== 200) {
    echo json_encode(['error' => 'upstream request failed', 'detail' => 'HTTP ' . $httpCode], JSON_UNESCAPED_UNICODE);
    exit;
}

$data = json_decode($raw, true);
$code = isset($data['code']) ? (int) $data['code'] : 0;

if ($code !== 200 || empty($data['playlist'])) {
    echo json_encode([
        'error'  => 'playlist not accessible',
        'detail' => (string) ($data['message'] ?? $data['msg'] ?? ('code ' . $code)),
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$playlist = $data['playlist'];
$tracks   = $playlist['tracks'] ?? [];

$items = [];
$seen  = [];
foreach ($tracks as $track) {
    if (count($items) >= $limit) {
        break;
    }
    $songId = isset($track['id']) ? (string) $track['id'] : '';
    if ($songId === '' || isset($seen[$songId])) {
        continue;
    }
    $seen[$songId] = true;

    $artists = [];
    if (!empty($track['ar']) && is_array($track['ar'])) {
        foreach ($track['ar'] as $artist) {
            if (!empty($artist['name'])) {
                $artists[] = (string) $artist['name'];
            }
        }
    } elseif (!empty($track['artists']) && is_array($track['artists'])) {
        foreach ($track['artists'] as $artist) {
            if (!empty($artist['name'])) {
                $artists[] = (string) $artist['name'];
            }
        }
    }

    $cover = '';
    if (!empty($track['al']['picUrl'])) {
        $cover = (string) $track['al']['picUrl'];
    } elseif (!empty($track['album']['picUrl'])) {
        $cover = (string) $track['album']['picUrl'];
    }

    // fee: 0 免费 / 1 VIP / 4 付费专辑 / 8 免费（含试听）
    $fee = array_key_exists('fee', $track) ? (int) $track['fee'] : 0;

    $items[] = [
        'id'     => $songId,
        'name'   => (string) ($track['name'] ?? ''),
        'artist' => implode(' / ', $artists),
        'url'    => 'https://music.163.com/song/media/outer/url?id=' . $songId . '.mp3',
        'cover'  => $cover,
        'vip'    => ($fee === 1),
    ];
}

$result = [
    'name'       => (string) ($playlist['name'] ?? ''),
    'cover'      => (string) ($playlist['coverImgUrl'] ?? ''),
    'url'        => 'https://music.163.com/#/playlist?id=' . $id,
    'trackCount' => count($items),
    'tracks'     => $items,
];

$json = json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

if (!is_dir($cacheDir)) {
    @mkdir($cacheDir, 0755, true);
}
if (is_dir($cacheDir) && is_writable($cacheDir)) {
    @file_put_contents($cacheFile, $json, LOCK_EX);
}

echo $json;
