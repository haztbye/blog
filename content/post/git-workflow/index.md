---
title: Git工作流分享
description: 自己在幂律和海尔学习到的关于git的使用心得
slug: git-workflow-guide
image: cover.webp
date: 2025-10-07
categories:
    - 技术笔记
tags:
    - Git
weight: 4
---

在使用GitHub和GitLab时，代码仓库的管理和使用对于开发来说很重要，这里分享一下我学到的Git工作流程和实践方法。

## Git基础知识

### 如果你对Git还不太熟悉

**强烈推荐这个学习网站**：[Learn Git](https://www.w3schools.com/git/default.asp)

这是一个Git学习网站，通过互动式关卡让你理解Git的核心概念。quiz必须拿到18/20 分，也就是说，必须全明白。

---

##  Git基础工作流

### 日常开发的核心命令

```bash
# 1. 查看状态
git status

# 2. 添加文件到暂存区
git add .              # 添加所有修改
git add file.txt       # 添加指定文件

# 3. 提交
git commit -m "提交信息"

# 4. 推送到远程
git push origin main

# 5. 拉取最新代码
git pull origin main
```

### 分支操作

```bash
# 查看分支
git branch              # 本地分支
git branch -a           # 所有分支

# 创建并切换分支
git checkout -b feature-name
# 或使用新命令
git switch -c feature-name

# 切换分支
git checkout main
git switch main

# 删除分支
git branch -d feature-name     # 安全删除
git branch -D feature-name     # 强制删除
```

---

## Git工作流

### 工作流程

#### 1. 分支策略

```
main（master）      ← 生产环境代码
  ↑
develop            ← 开发环境代码
  ↑
feature/xxx        ← 功能开发分支
hotfix/xxx         ← 紧急修复分支
```

**分支命名规范**：
- `feature/user-login` - 功能分支
- `bugfix/fix-upload` - bug修复
- `hotfix/urgent-fix` - 紧急修复
- `release/v1.0.0` - 发布分支

#### 2. 完整开发流程

第一阶段：初始设置 & 克隆项目

1. 克隆远程仓库（首次获取项目）
git clone 

cd 项目名

2. 查看所有分支（本地+远程）
git branch -avv

3. 创建并切换到个人开发分支（基于最新master）
git checkout master             # 进入主分支
git pull origin master          # 更新主分支
git checkout -b name/功能描述    # 创建个人分支

4. 推送分支并建立跟踪关系（关键步骤！）
git push -u origin name/功能描述

第二阶段：日常开发工作流 

1. 每日开始工作前（必做）
git checkout zts/功能描述      # 切换到个人分支
git fetch --all               # 获取所有远程更新
git merge origin/master       # 合并主分支最新代码

2. 开发过程中...
# 修改文件后保存（正常使用编辑器）

3. 查看修改状态
git status

4. 添加修改到暂存区
git add 文件名                 # 添加特定文件
git add .                     # 添加所有修改（不含删除）
git add -A                    # 添加所有修改（包含删除）

5. 提交到本地仓库
git commit -m "清晰的提交说明"
 提交说明规范：
   feat: 新功能
   fix: 修复bug
   docs: 文档更新
   refactor: 重构代码
   test: 测试用例

6. 推送代码到远程
git push


##  Code Review流程

### CR实践

1. **提交PR前的自查**
   ```bash
   # 确保代码格式正确
   npm run lint
   
   # 运行测试
   npm run test
   
   # 查看改动
   git diff develop
   ```

2. **PR描述模板**
   ```markdown
   ## 功能描述
   添加了...功能
   
   ## 修改内容
   - [ ] 新增...模块
   - [ ] 添加单元测试
   - [ ] 更新文档
   
   ## 测试说明

   
   ## 相关issue

   ```

3. **响应Review意见**
   ```bash
   # 修改后追加提交
   git add .
   git commit -m "fix: 根据review意见修改"
   git push origin feature-branch
   ```

---

##  冲突解决

### 合并冲突的处理

```bash
# 1. 拉取最新代码发现冲突
git pull origin develop
# Auto-merging file.txt
# CONFLICT (content): Merge conflict in file.txt

# 2. 查看冲突文件
git status

# 3. 手动解决冲突
# 打开文件，会看到：
# <<<<<<< HEAD
# 你的修改
# =======
# 别人的修改
# >>>>>>> branch-name

# 4. 修改完成后
git add file.txt
git commit -m "解决合并冲突"

# 5. 推送
git push origin feature-branch
```

### 预防冲突的技巧

```bash
# 开发前先同步最新代码
git checkout develop
git pull origin develop
git checkout feature-branch
git rebase develop

# 频繁提交，小步快跑
# 及时push，让团队知道你的进度
```

---

##  踩过的坑

### 1. 不要在主分支直接开发

 **错误做法**：
```bash
git checkout main
# 直接在main上改代码
git commit -m "fix bug"
```

 **正确做法**：
```bash
git checkout main
git checkout -b hotfix/urgent-fix
# 在新分支修改
git commit -m "fix: 紧急修复"
# 通过PR合并
```

### 2. commit信息要有意义

 **烂提交信息**：
```bash
git commit -m "修改"
git commit -m "update"
git commit -m "fix bug"
```

 **好的提交信息**：
```bash
git commit -m "feat(parser): 添加PDF文本提取功能"
git commit -m "fix(upload): 修复大于10MB文件上传失败的问题"
```

### 3. 不要提交大文件和敏感信息

```bash
# 使用.gitignore
echo "*.log" >> .gitignore
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore

# 如果不小心提交了
git rm --cached sensitive_file
git commit -m "移除敏感文件"
```

### 4. 定期同步远程仓库

```bash
# 每天开始工作前
git checkout develop
git pull origin develop

# 每次开发前
git checkout feature-branch
git rebase develop
```

---

## 📝 实用Git别名配置

提高效率的Git快捷命令：

```bash
# 配置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --graph --oneline --decorate --all"

# 使用
git st        # 等于 git status
git co main   # 等于 git checkout main
git lg        # 漂亮的日志
```

---

##  总结

### Git工作流的核心原则

1. **小步提交** - 功能拆分，频繁commit
2. **清晰分支** - 命名规范，职责明确
3. **规范信息** - commit message要有意义
4. **及时同步** - 经常pull，避免冲突
5. **代码审查** - PR流程不能省


**最大的感悟**：
> Git是团队协作的规范。好的Git使用习惯，能让自己的代码更清晰，也不用背那么多锅QWQ

---

下篇写啥好呢？正则还是什么呢，要不不写技术文档了，学到再写，嘿嘿

