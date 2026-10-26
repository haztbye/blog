# 考研日志（加密）

这一套东西的作用：把**每周六晚上**写下的备考日志，用你自己的密码加密后放进博客。
对外看起来是一篇「马赛克 + 锁」的帖子，只有输入密码才能在浏览器里看到正文。

## 目录结构

| 位置 | 内容 | 是否进 git |
|---|---|---|
| `study-log-private/kaoyan-log.md`（仓库**外**，`blogger/study-log-private/`） | 明文日志 | ❌ 不进 |
| `%USERPROFILE%\.huanhe-study-key` | 你的密码 | ❌ 不进 |
| `my-blog/data/study-log.yaml` | 加密后的密文（salt / iv / ct） | ✅ 进（只是密文） |

> 也就是说：**密文反而成了你的备份**——push 到 GitHub 后，即使本机硬盘坏了，
> 只要有密码就能把日志解出来。但明文和密码务必自己留一份（密码建议存密码管理器）。

## 每周流程

1. 周六晚上把这一周的事和想法写进 `study-log-private/kaoyan-log.md`（新的一篇放在**最上面**，
   用 `## 2026-11-01 第 N 周` 这样的二级标题开头）
2. 双击 `my-blog/tools/study-log/publish-log.bat`
3. 等一分钟，刷新博客，输入密码即可看到最新内容

脚本会：加密明文 → 覆盖 `data/study-log.yaml` → 调用 `publish.bat` 提交并推送。

## 首次使用

1. 双击 `tools/study-log/set-key.bat`，输入密码（至少 8 位，输入时不显示）
2. 运行一次 `publish-log.bat`

## 安全说明（重要）

- 加密方案：PBKDF2-HMAC-SHA256（21 万次）派生密钥 + AES-256-GCM 认证加密
- 密码**只在本机**，不进仓库、不进聊天记录；忘记密码 → 内容无法解密（明文还在，可以重新加密）
- 页面解锁后在 `sessionStorage` 里记住密码，**关掉标签页即失效**；点了「锁定」也会清掉
- 浏览器解密要求 **HTTPS**（本站已启用）；若用 http 打开会提示不支持
- 密文是公开的，安全性 = 密码强度。**别用生日、手机号、`12345678` 这类**

## 排查

| 现象 | 原因 / 处理 |
|---|---|
| 页面显示「密码不对」 | 输错了，或本机密码文件被改过（重新 `set-key.bat` + `publish-log.bat`） |
| 页面显示「日志数据还没生成」 | 还没跑过 `publish-log.bat` |
| `No Python with the 'cryptography' package found` | 设环境变量 `STUDY_LOG_PY` 指向可用的 python.exe |
| 想换密码 | 重新 `set-key.bat`，再跑 `publish-log.bat`（用新密码重新加密一次） |