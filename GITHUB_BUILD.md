# 使用 GitHub Actions 构建 Android APK

## 方法步骤

### 1. 创建 GitHub 仓库

在 GitHub 上创建一个新仓库，例如：`kivy-ai-chat`

### 2. 初始化 Git 仓库

```bash
cd f:/kivy
git init
git add .
git commit -m "Initial commit: Kivy AI Chat Assistant"
```

### 3. 推送到 GitHub

```bash
git remote add origin https://github.com/你的用户名/kivy-ai-chat.git
git branch -M main
git push -u origin main
```

### 4. 自动构建

代码推送后，GitHub Actions 会自动开始构建 APK。

### 5. 下载 APK

1. 访问 GitHub 仓库页面
2. 点击 **Actions** 标签
3. 选择最新的构建任务
4. 在 **Artifacts** 部分下载 `android-apk`

## 手动触发构建

在仓库页面：
1. 点击 **Actions** 标签
2. 选择 **Build Android APK** 工作流
3. 点击 **Run workflow** 按钮

## APK 位置

构建成功后，APK 文件位于：
```
bin/kvyaichat-0.1-arm64-v8a-debug.apk
```

## 安装 APK

将 APK 传输到 Android 手机后，直接安装即可。

---

## 注意事项

- 首次构建可能需要 20-30 分钟
- 需要 GitHub 账号（免费账户足够）
- 确保代码已推送到 main 分支
