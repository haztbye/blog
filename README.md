# 去看花海的路上 · Huanhe 的博客

个人博客的源码仓库。

- 线上地址：<https://huanhe.site>
- 内容方向：学习记录、生活随笔、考研路上的碎碎念

## 技术栈

| 部分 | 说明 |
|---|---|
| 生成器 | [Hugo](https://gohugo.io/) extended 0.149.0 |
| 主题 | [Hugo Theme Stack](https://github.com/CaiJimmy/hugo-theme-stack) v3.31（通过 Hugo Modules 引入） |
| 自定义外观 | `assets/scss/custom.scss`：薄暮花海渐变背景、玻璃拟态卡片、衬线标题、渐变胶囊等 |
| 模板覆盖 | `layouts/partials/`：回到顶部按钮、主题色、iOS 图标、去掉 Google Fonts 请求 |
| 部署 | 自写的增量部署脚本：本地/远端 MD5 对比，只上传有变化的文件 |

## 本地开发

前置：Hugo extended、Git。

```bash
cd my-blog
hugo server --disableFastRender
```

打开 <http://localhost:1313> 预览，保存文件后自动刷新。

## 写文章

在 `content/post/<目录名>/index.md` 新建文章，front matter 示例：

```yaml
---
title: 标题
description: 一句话摘要（会显示在首页卡片和搜索结果）
slug: english-slug
image: cover.webp        # 可选：把封面图命名为 cover.webp 放进同一目录
date: 2026-10-23
categories:
    - 生活随笔
tags:
    - 个人成长
---
```

正文里 `##` / `###` 小标题会自动生成右侧目录。

## 部署

部署由 **GitHub Actions** 自动完成（`.github/workflows/deploy.yml`）：

```
改内容 → 双击 publish.bat（提交 + 推送）→ GitHub 自动构建并同步到服务器 → 刷新网站
```

- 只有 push 到 `master` 才会触发；也可在仓库 Actions 页手动点 `Run workflow`
- 推完约 1~2 分钟生效，进度看 <https://github.com/haztbye/blog/actions>
- 需要的仓库 Secrets：`SERVER_HOST`、`SERVER_USER`、`SERVER_SSH_KEY`，可选 `SERVER_PORT`（默认 22）
- 同步用 `rsync --delete`，但会保留服务器上的 `.user.ini` / `.htaccess` / `.well-known/`

本地曾经用过的 `deploy-blog.ps1/.bat`（增量上传脚本）现在只是**应急备用**，正常流程用不到，也可以删掉。

本地预览不受影响：

```bash
hugo server
```


## 目录结构

```
.
├── assets/            # 自定义 SCSS 与图片（头像等）
├── config/_default/   # 站点配置：config / params / menu / module / markup / permalinks
├── content/           # 文章与页面
│   ├── post/          # 文章
│   └── page/          # 归档、搜索、关于
├── layouts/           # 覆盖主题的局部模板
├── static/            # 原样输出的文件（favicon、分享图等）
├── deploy-blog.ps1    # 增量部署脚本（deploy-blog.bat 是双击入口）
├── publish.bat        # 一键发布：提交 + 推送 + 部署
└── guide.md           # 本地开发/部署速查
```

## 首页与导航

- **顶部胶囊导航**：`layouts/partials/sidebar/left.html`（覆盖主题原来的左侧栏，保留主题 JS 需要的 `#toggle-menu` / `#main-menu` / `#dark-mode-toggle`）
- **首页全屏 Hero**（照片轮播 + 站名 + 语录）：`layouts/index.html` + `config/_default/params.toml` 里的 `[hero]`
- **文章网格列表**：`assets/scss/custom.scss` 中的 `.article-grid`（首页 3 列 / 平板 2 列 / 手机 1 列）

### 换照片、改语录

1. 把照片放进 `static/img/hero/`（建议 1920×1080 横图，命名 `slide-1.jpg` 起，按顺序轮播）
2. 在 `params.toml` 里改/加：

```toml
[[hero.slides]]
src = "/img/hero/slide-1.jpg"

[[hero.quotes]]
text = "想写的话"
author = "署名"        # 没有出处就省略这一行
```

整体开关是 `[hero]` 下的 `enable`，切换间隔是 `interval`（毫秒）。

首页背景行为：照片固定铺满整页，向下滚动时背景逐渐**模糊 + 磨砂**（浅色主题磨砂白、深色主题暗玻璃），滚回顶部恢复清晰。实现见 `custom.scss` 的 `.hero-bg-blur` / `.hero-tint`。

## 说明

- `public/`、`resources/` 是构建产物与缓存，不提交到仓库。
- 主题通过 Hugo Modules 引入，升级主题后建议本地预览确认自定义样式仍然正常。
- 文章内容采用 CC BY-NC-SA 4.0 授权（见站点文章页脚）。
