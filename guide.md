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

旧的本地部署脚本（`deploy-blog.ps1` / `deploy-blog.bat`）已删除。若 GitHub Actions 长期不可用，可从 git 历史恢复：

```bash
git log --all --oneline -- deploy-blog.ps1
git show <commit>:deploy-blog.ps1 > deploy-blog.ps1
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
- 照片放在 `static/img/hero/`（建议 1920×1080），语录在 `params.toml` 的 `[[hero.quotes]]`
- 节奏参数：`interval`（照片轮换）、`type_speed`（打字）、`hold_ms`（停留）、`delete_speed`（逐字删除），单位毫秒
- 文章网格：`assets/scss/custom.scss` 里的 `.article-grid`

## 服务器 nginx 配置说明

`huanhe.site` 的站点配置（`/www/server/panel/vhost/nginx/huanhe.site.conf`）里手动加过两处优化，**不在 git 里**：

- 图片/图标/字体缓存 30 天；带内容指纹的 JS/CSS 缓存 1 年（`immutable`）
- `gzip_comp_level 5`（全局 gzip 已开，这里提高压缩级别）

改动前的备份在 `/www/server/panel/vhost/nginx/huanhe.site.conf.bak.*`。

⚠️ 在宝塔面板里"保存"站点设置可能会覆盖这些改动；如果发现 CSS/JS 的缓存头变回 12h，说一声重新加即可。

## 私有学习面板（/me/）

- 地址：`https://huanhe.site/me/`，Nginx 基本认证（密码文件 `*.htpasswd`，见 `blogger/private/README.md`）
- 数据与生成脚本在 **仓库之外**：`blogger/private/`（`study.json` → `build_study.py` → `dist/index.html` → scp 上传）
- 服务器目录：旧服务器 `/www/wwwroot/private/`；腾讯新服务器用 `/var/www/private/`
- ⚠️ 服务器上的 Nginx `/me/` 配置**不在 git 里**，换服务器后要重新加一次（含 `.htpasswd`）

## 目录说明

- `content/`：文章与页面（`post/` 文章，`page/` 归档/搜索/关于）
- `assets/scss/custom.scss`：自定义主题样式（薄暮花海 + 玻璃拟态）
- `layouts/`：覆盖主题的局部模板（回到顶部、主题色、iOS 图标、字体加载）
- `config/_default/`：站点配置（`config.toml`、`params.toml`、`menu.toml` 等）
- `static/`：原样拷贝到站点根目录的文件（favicon、分享图）
- `publish.bat`：一键发布（提交 + 推送，随后 GitHub Actions 自动部署）
- `public/`、`resources/`：构建产物/缓存，已被 `.gitignore` 排除，不提交

## 服务器初始化

首次配置服务器 SSH 密钥用的 `setup-server.bat` **不在本仓库**（含敏感信息），请只在本地保管，不要提交或上传。
