# 本地开发与发布速查

## 本地预览

```bash
cd /d/123pan/python/py\ \ \ exercises/blogger/my-blog
hugo server --disableFastRender
```

浏览器打开 http://localhost:1313 ，改文件保存后自动刷新。

## 一键发布（推荐）

双击仓库目录里的 **publish.bat**：git 提交 → 推送 GitHub → 构建并部署上线。

也可以在命令行带提交说明运行：

```bat
publish.bat "update: 新增一篇文章"
```

## 只部署（不提交 git）

双击 **deploy-blog.bat**，默认增量：只上传有变化的文件。

可用参数：

- `-DryRun` 只对比并显示"要上传 / 要删除"的清单，不动服务器
- `-Full` 忽略差异全部重传（保险模式）
- `-NoDelete` 只上传，不删除服务器上多余的文件

原理：hugo 构建 → 本地文件算 MD5 → ssh 读取服务器文件 MD5 → 只传差异 → 修权限 → 内容校验。
服务器根目录的 `.user.ini` / `.htaccess` / `.well-known` 等文件受保护，不会被删除。

## 手动 git 流程

```bash
git add -A
git commit -m "改了什么"
git push
```

仓库：https://github.com/haztbye/blog

## 目录说明

- `content/`：文章与页面（`post/` 文章，`page/` 归档/搜索/关于）
- `assets/scss/custom.scss`：自定义主题样式（薄暮花海 + 玻璃拟态）
- `layouts/`：覆盖主题的局部模板（回到顶部、主题色、iOS 图标、字体加载）
- `config/_default/`：站点配置（`config.toml`、`params.toml`、`menu.toml` 等）
- `static/`：原样拷贝到站点根目录的文件（favicon、分享图）
- `deploy-blog.ps1` / `deploy-blog.bat` / `publish.bat`：部署脚本（Hugo 主程序在该仓库的上一级目录）
- `public/`、`resources/`：构建产物/缓存，已被 `.gitignore` 排除，不提交

## 服务器初始化

首次配置服务器 SSH 密钥用的 `setup-server.bat` **不在本仓库**（含敏感信息），请只在本地保管，不要提交或上传。
