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

推荐双击 `publish.bat`：**提交 + 推送 GitHub + 构建部署** 一次完成。

也可以分开：

- `deploy-blog.bat`：只做部署（增量上传；`-DryRun` 可预览差异、`-Full` 全量重传、`-NoDelete` 不删多余文件）
- 手动 git：`git add -A && git commit -m "..." && git push`

部署脚本原理：hugo 构建 → 本地文件算 MD5 → ssh 读取服务器文件 MD5 → 只传差异 → 修权限 → 内容校验。
服务器根目录的 `.user.ini` / `.htaccess` / `.well-known` 等文件受保护，不会被删除。

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

## 说明

- `public/`、`resources/` 是构建产物与缓存，不提交到仓库。
- 主题通过 Hugo Modules 引入，升级主题后建议本地预览确认自定义样式仍然正常。
- 文章内容采用 CC BY-NC-SA 4.0 授权（见站点文章页脚）。
