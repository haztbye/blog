# 本地开发与发布速查

## 本地预览

```bash
cd /d/123pan/python/py\ \ \ exercises/blogger/my-blog
hugo server --disableFastRender
```

浏览器打开 http://localhost:1313 ，改文件保存后自动刷新。

## 发布（GitHub Actions 自动部署）

1. 改内容（本地可用 `hugo server` 预览）
2. 双击 **`publish.bat`**：只做 `git add / commit / push`
3. GitHub Actions 自动构建并同步到服务器（约 1~2 分钟）
4. 刷新 https://huanhe.site 查看；进度看 https://github.com/haztbye/blog/actions

说明：

- 只有 push 到 `master` 才触发部署；也可以在 Actions 页手动 `Run workflow`
- 需要的仓库 Secrets：`SERVER_HOST`、`SERVER_USER`、`SERVER_SSH_KEY`，可选 `SERVER_PORT`（默认 22）
- 服务器上的 `.user.ini` / `.htaccess` / `.well-known/` 不会被删除

旧的 `deploy-blog.ps1` / `deploy-blog.bat` 是本地增量上传脚本，现在仅作应急备用，正常流程用不到。

## 只部署（应急，不推荐日常用）

若 GitHub Actions 不可用，可临时用：

```bat
deploy-blog.bat            :: 增量上传
deploy-blog.bat -DryRun    :: 只预览差异
```

## 手动 git 流程

```bash
git add -A
git commit -m "改了什么"
git push
```

仓库：https://github.com/haztbye/blog

## 首页外观

- 顶部胶囊导航：`layouts/partials/sidebar/left.html`
- 首页全屏 Hero：`layouts/index.html` + `config/_default/params.toml` 的 `[hero]`
- 照片放在 `static/img/hero/`（建议 1600×900），语录在 `params.toml` 的 `[[hero.quotes]]`
- 文章网格：`assets/scss/custom.scss` 里的 `.article-grid`

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
