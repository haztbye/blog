---
title: 如何SSH远程连接服务器
description: 对于服务器连接的一些心得，云服务器的连接也是相通的
slug: ssh-guide
image: cover.webp
date: 2025-10-10
categories:
    - 技术笔记
tags:
    - SSH
weight: 3
---

在幂律实习的时候，第一次接触到服务器连接，从一开始的手忙脚乱到后来的得心应手，这里总结一下我学到的服务器连接方法，尤其是SSH

## 🤔 SSH是什么？

SSH（Secure Shell）是一种网络协议，用于在不安全的网络中安全地访问远程计算机。

**简单来说**：就是让你能在自己电脑上操作远程服务器的工具。

**为什么要用SSH？**
-  **安全**：数据传输加密
-  **方便**：直接在命令行操作服务器
-  **强大**：可以传输文件、端口转发等

---

##  基础连接方法

### 最简单的连接命令

```bash
ssh username@server_ip
```

**示例**：
```bash
ssh root@192.168.1.100
```

然后输入密码就能连接了，这种连接方式也就是最普通的密码连接。

### 指定端口连接

```bash
ssh -p 端口号 username@server_ip
```

**示例**：
```bash
ssh -p 22022 root@192.168.1.100
```
用于端口不是默认端口（22）的情况

---

##  公钥密钥认证（此乃重中之重）

### 为什么要用密钥而不是密码？

1. **更安全** - 密钥比密码难破解得多
2. **更方便** - 不用每次输入密码
3. **更专业** - 在我实习中的两家企业，都这么干

### 生成SSH密钥对

在**本地电脑**上执行：

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

**参数解释**：
- `-t rsa`：使用RSA加密算法
- `-b 4096`：密钥长度4096位（更安全）
- `-C`：注释，通常写邮箱

**执行过程**：
```bash
# 1. 询问密钥保存位置（直接回车用默认）
Enter file in which to save the key (/Users/你的用户名/.ssh/id_rsa):

# 2. 询问是否设置密码（可以直接回车跳过）
Enter passphrase (empty for no passphrase):

# 3. 再次确认密码
Enter same passphrase again:
```

**生成的文件**：
- `~/.ssh/id_rsa` - 私钥（千万不要泄露！）
- `~/.ssh/id_rsa.pub` - 公钥（可以随便给）

### 将公钥上传到服务器

**方法一：使用 `ssh-copy-id`（推荐）**
下面会讲这种方法的具体原理和使用说明

```bash
ssh-copy-id username@server_ip 
```

**方法二：手动上传**

```bash
# 1. 查看公钥内容
cat ~/.ssh/id_rsa.pub

# 2. 复制输出的内容

# 3. 登录服务器，将公钥添加到授权文件
ssh username@server_ip
mkdir -p ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 测试密钥登录

```bash
ssh username@server_ip
```

如果不需要输入密码就登录成功了，说明配置成功了

---

##  配置SSH Config文件

### 为什么要配置Config？

每次都要输入 `ssh user@192.168.1.100 -p 22022` 太麻烦了！

配置后只需要：`ssh myserver` ✨

### 创建/编辑Config文件

```bash
# Windows
notepad ~/.ssh/config

# Mac/Linux
vim ~/.ssh/config
```

### 配置示例

```bash
# 服务器1 
Host GPU002
    HostName 192.168.1.100
    User your_username
    Port 22
    IdentityFile ~/.ssh/id_rsa

# 服务器2 - 测试服务器
Host test-server
    HostName test.example.com
    User root
    Port 22022
    IdentityFile ~/.ssh/id_rsa_test

# 服务器3 - 使用跳板机
Host jump-server
    HostName final.server.com
    User admin
    ProxyJump jump.server.com
```

**配置参数说明**：
- `Host`：别名，随便起（之后用这个连接）
- `HostName`：真实的服务器地址（IP或域名）
- `User`：登录用户名
- `Port`：端口号（默认22可以不写）
- `IdentityFile`：私钥文件路径
- `ProxyJump`：跳板机（如果需要通过跳板机连接，至于跳板机是什么，感兴趣的可以自行了解一下，企业运维中较为多见）

### 使用配置好的连接

```bash
# 直接用别名连接
ssh GPU002

# 传输文件也方便了
scp myfile.txt GPU002:~/
```

---

##  常见问题与解决

### 1. Permission denied (publickey)

**原因**：权限问题或公钥没配置好

**解决**：
```bash
# 检查服务器上的权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 确认公钥已添加
cat ~/.ssh/authorized_keys
```

### 2. Connection timeout

**原因**：
- 服务器IP错误
- 防火墙拦截
- 服务器SSH服务未启动

**解决**：
```bash
# 测试网络连通性
ping server_ip

# 测试端口是否开放
telnet server_ip 22
```

### 3. WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!

**原因**：服务器重装或IP被其他机器占用

**解决**：
```bash
# 删除旧的主机指纹
ssh-keygen -R server_ip
```

### 4. 密钥失效

**原因**：服务器上的 `authorized_keys` 被修改或删除

**解决**：
```bash
# 重新上传公钥
ssh-copy-id username@server_ip
```

---

## 实战案例：配置个人服务器

### 背景

搭建这个博客时，我租了一个云服务器，需要连接上去部署网站，所以也在这里分享一下是如何进行云服务器连接的

### 服务器信息

- **公网IP**：your-server-ip
- **用户名**：root
- **初始密码**：（当时好像是连接了xshell进行连接，然后生成了初始密码？我不太确定哈）

### 完整配置过程

#### 1. 生成专用密钥

```bash
# 为博客服务器生成专用密钥
ssh-keygen -t rsa -b 4096 -C "huanhe@blog" -f ~/.ssh/id_rsa_blog

# Windows用户
ssh-keygen -t rsa -b 4096 -C "huanhe@blog" -f %USERPROFILE%\.ssh\id_rsa_blog
```

**为什么用专用密钥？**
- 不同服务器用不同密钥，更安全
- 一个密钥泄露不影响其他服务器

#### 2. 上传公钥到服务器

**方法1：使用 ssh-copy-id（推荐！）**

```bash
# Linux/Mac
ssh-copy-id -i ~/.ssh/id_rsa_blog.pub root@your-server-ip

# Windows（需要安装OpenSSH）
type %USERPROFILE%\.ssh\id_rsa_blog.pub | ssh root@your-server-ip "cat >> ~/.ssh/authorized_keys"
```

**ssh-copy-id 做了什么？**
1. 读取你的公钥文件
2. 连接到远程服务器（需要输入密码）
3. 在服务器上创建 `~/.ssh` 目录（如果不存在）
4. 将公钥追加到 `~/.ssh/authorized_keys`
5. 设置正确的权限（700 和 600）

**方法2：手动上传（我以前的做法）**

```bash
# 1. 首次密码登录
ssh root@your-server-ip

# 2. 创建SSH目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 3. 编辑授权文件
vim ~/.ssh/authorized_keys
# 粘贴公钥内容，保存退出

# 4. 设置权限
chmod 600 ~/.ssh/authorized_keys

# 5. 退出
exit
```

**对比：**
- **ssh-copy-id**：一条命令搞定 
- **手动上传**：需要5步，容易出错

#### 3. 配置SSH Config

编辑 `~/.ssh/config`：

```bash
# 博客服务器
Host blog
    HostName your-server-ip
    User root
    Port 22
    IdentityFile ~/.ssh/id_rsa_blog
    
# 可选：保持连接
Host blog
    HostName your-server-ip
    User root
    IdentityFile ~/.ssh/id_rsa_blog
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

#### 4. 测试连接

```bash
# 简单！
ssh blog

# 第一次连接会提示确认指纹
The authenticity of host 'your-server-ip' can't be established.
ECDSA key fingerprint is SHA256:xxxxxx.
Are you sure you want to continue connecting (yes/no)? yes

# 之后就不需要输入密码了
Welcome to Ubuntu 22.04 LTS
root@server:~#
```

#### 5. 修改服务器密码（安全）

```bash
# 连接后立即修改
ssh blog
passwd

# 输入新密码两次
New password: ********
Retype new password: ********
passwd: password updated successfully
```

#### 6. 一键部署脚本

创建 `deploy-blog.bat`：

```bash
@echo off
echo 部署博客...

REM 1. 生成静态文件
hugo --minify

REM 2. 上传到服务器
scp -r public/* blog:/www/wwwroot/huanhe.site/

REM 3. 设置权限
ssh blog "chown -R www:www /www/wwwroot/huanhe.site"

echo 部署完成
```

**以后更新博客只需双击运行脚本就可以** 


---

##  深入理解：ssh-copy-id

### ssh-copy-id 是什么？

`ssh-copy-id` 是一个脚本工具，用于将你的公钥安全地复制到远程服务器。

### 基本用法

```bash
# 基本语法
ssh-copy-id [选项] [用户名@]主机名

# 常用示例
ssh-copy-id root@192.168.1.100              # 使用默认密钥
ssh-copy-id -i ~/.ssh/id_rsa_blog.pub user@server  # 指定密钥
ssh-copy-id -p 2222 user@server             # 指定端口
```

### 工作原理

```bash
# 当你运行 ssh-copy-id 时，它做了这些事：

1. 读取本地公钥文件
   ├─ 默认：~/.ssh/id_rsa.pub
   └─ 指定：-i 参数指定的文件

2. 连接到远程服务器
   └─ 需要你输入密码（最后一次）

3. 在服务器上执行
   mkdir -p ~/.ssh                    # 创建目录
   chmod 700 ~/.ssh                   # 设置目录权限
   cat >> ~/.ssh/authorized_keys      # 追加公钥
   chmod 600 ~/.ssh/authorized_keys   # 设置文件权限

4. 完成
   └─ 下次连接不再需要密码
```

### 常见选项

```bash
# -i 指定公钥文件
ssh-copy-id -i ~/.ssh/id_rsa_blog.pub root@server

# -p 指定端口
ssh-copy-id -p 22022 root@server

# -f 强制模式（即使已有密钥也追加）
ssh-copy-id -f -i ~/.ssh/id_rsa.pub root@server

# -n 试运行（只显示要做什么，不实际执行）
ssh-copy-id -n root@server

# -o 传递SSH选项
ssh-copy-id -o "StrictHostKeyChecking=no" root@server
```

### Windows 用户的解决方案

**问题**：Windows 默认没有 `ssh-copy-id`

**解决方案1：安装 Git Bash**

Git for Windows 自带 `ssh-copy-id`：

```bash
# 在Git Bash中
ssh-copy-id -i ~/.ssh/id_rsa_blog.pub root@server
```

### 多密钥管理

```bash
# 为不同服务器生成不同密钥
ssh-keygen -t rsa -f ~/.ssh/id_rsa_github
ssh-keygen -t rsa -f ~/.ssh/id_rsa_company
ssh-keygen -t rsa -f ~/.ssh/id_rsa_blog

# 分别上传
ssh-copy-id -i ~/.ssh/id_rsa_github.pub git@github.com
ssh-copy-id -i ~/.ssh/id_rsa_company.pub user@company-server
ssh-copy-id -i ~/.ssh/id_rsa_blog.pub root@blog-server

# 在Config中配置
Host github.com
    IdentityFile ~/.ssh/id_rsa_github

Host company
    IdentityFile ~/.ssh/id_rsa_company
    
Host blog
    IdentityFile ~/.ssh/id_rsa_blog
```

### 常见问题

**1. Permission denied after ssh-copy-id**

```bash
# 检查服务器权限
ssh root@server
ls -la ~/.ssh

# 应该是：
# drwx------ (700) .ssh/
# -rw------- (600) .ssh/authorized_keys

# 如果不对，修复：
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**2. Still asking for password**

```bash
# 检查SSH配置
ssh -v root@server  # 查看详细日志

# 可能原因：
# - 服务器禁用了密钥认证
# - 使用了错误的密钥
# - SELinux问题（CentOS）

# 服务器上检查
sudo vim /etc/ssh/sshd_config

# 确保这些配置：
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

**3. Too many authentication failures**

```bash
# 原因：密钥太多，SSH尝试了所有密钥
# 解决：在Config中明确指定
Host blog
    IdentitiesOnly yes
    IdentityFile ~/.ssh/id_rsa_blog
```

---

## 📝 写在最后

SSH看起来复杂，但掌握了就会发现也并不难，这是连接服务器进行开发的基础，切忌囫囵吞枣。

下次写写在幂律学到的Git工作流，这也是进行企业开发的基础第一步

---

