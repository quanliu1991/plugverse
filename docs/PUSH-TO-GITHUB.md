# PlugVerse 推送到 GitHub 指南

## 📝 步骤 1：在 GitHub 创建仓库

1. 访问：https://github.com/new
2. 填写信息：
   - **Repository name:** `plugverse`
   - **Description:** 🌌 插件化客户平台 - Plugin-based Customer Platform
   - **Visibility:** Public（公开）或 Private（私有）
   - ❌ 不要勾选 "Add a README file"
   - ❌ 不要勾选 "Add .gitignore"
   - ❌ 不要勾选 "Choose a license"
3. 点击 "Create repository"

## 📝 步骤 2：关联远程仓库并推送

创建仓库后，在终端执行以下命令：

```bash
cd /Users/macstudio/.openclaw/workspace/plugverse

# 添加远程仓库（替换 YOUR_GITHUB_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/quanliu1991/plugverse.git

# 验证远程仓库
git remote -v

# 推送到 GitHub
git push -u origin main
```

## 📝 步骤 3：验证推送

推送成功后，访问：https://github.com/quanliu1991/plugverse

你应该能看到所有文件和初始提交。

## 🔐 使用 SSH（可选，推荐）

如果你配置了 SSH 密钥，可以使用 SSH 方式：

```bash
# 移除 HTTPS 远程
git remote remove origin

# 添加 SSH 远程
git remote add origin git@github.com:quanliu1991/plugverse.git

# 推送
git push -u origin main
```

## 📋 完整命令速查

```bash
# 进入项目目录
cd /Users/macstudio/.openclaw/workspace/plugverse

# 配置 Git 用户（已完成）
git config user.name "刘全"
git config user.email "18646313696@163.com"

# 添加远程仓库
git remote add origin https://github.com/quanliu1991/plugverse.git

# 推送
git push -u origin main

# 查看状态
git status

# 查看提交历史
git log --oneline
```

## ✅ 推送成功后

你的项目将出现在：
- **仓库地址:** https://github.com/quanliu1991/plugverse
- **克隆地址:** `git clone https://github.com/quanliu1991/plugverse.git`

---

**现在请执行步骤 2 的命令完成推送！** 🚀
