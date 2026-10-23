# 本地开发与部署指南

## 本地预览

进入站点目录（Git Bash）：

```bash
cd /d/123pan/python/py\ \ \ exercises/blogger/my-blog
hugo server --disableFastRender
```

然后浏览器打开 http://localhost:1313 ，用编辑器改内容/样式，保存后页面自动刷新。

## 一键部署

双击工作区根目录的 `deploy-blog.bat`（脚本本体是同目录的 `deploy-blog.ps1`）。

- 默认：**增量部署**，只上传有变化的文件、删除服务器上多余的文件
- `-DryRun`：只对比并显示"要上传 / 要删除"的清单，不动服务器
- `-Full`：忽略差异，全部重传（保险模式）
- `-NoDelete`：只上传，不删除服务器上多余的文件

原理：hugo 构建 → 本地文件算 MD5 → ssh 读取服务器文件 MD5 → 只传差异 → 修权限 → 内容校验。

注意：服务器根目录的 `.user.ini` / `.htaccess` / `.well-known` 等文件受保护，不会被删除，权限也自动跳过。

## 版本控制

仓库：https://github.com/haztbye/blog

改完内容后：

```bash
git add -A
git commit -m "写点这次改了什么"
git push
```

## 目录说明

- `content/`：文章与页面（`post/` 是文章，`page/` 是归档/搜索/关于等）
- `assets/scss/custom.scss`：自定义样式（薄暮花海主题）
- `layouts/`：覆盖主题的局部模板（回到顶部、主题色、图标、字体加载等）
- `config/_default/`：站点配置（`config.toml` 基础、`params.toml` 主题参数、`menu.toml` 菜单与社交链接）
- `static/`：原样拷贝到站点根目录的文件（favicon、分享图等）
- `public/`、`resources/`：构建产物/缓存，已被 `.gitignore` 排除，不提交
