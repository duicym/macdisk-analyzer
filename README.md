# macOS 磁盘空间分析工具

🛠️ 精准诊断 macOS「系统数据」占用过大的问题

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-blue.svg)](https://www.apple.com/macos/)

## 🎯 这个工具解决什么问题？

macOS 的「系统数据」类别经常莫名其妙占用几十 GB，但系统自带工具只告诉你"系统数据"，不告诉你具体是什么。

这个工具帮你：
- 🔍 精确定位系统数据占用的源头
- 📊 列出 Application Support 中最大的应用
- 🗑️ 识别可安全清理的缓存和临时文件
- 💾 给出具体的清理建议

## ✨ 功能特点

- **无需 sudo**：普通用户权限即可运行大部分分析
- **Apple Silicon 支持**：兼容 M1/M2/M3/M4 Mac
- **结构化报告**：输出清晰的分类报告
- **清理建议**：区分低/中/高风险清理操作

## 🚀 快速开始

### 一键分析

```bash
# 下载并运行
curl -fsSL https://raw.githubusercontent.com/mawenjun/macdisk-analyzer/main/scripts/analyze.py | python3
```

或者：

```bash
# 克隆仓库
git clone https://github.com/duicym/macdisk-analyzer.git
cd macdisk-analyzer

# 运行分析
python3 scripts/analyze.py
```

## 📊 典型输出

```
╔══════════════════════════════════════════════════════════╗
║     macOS 磁盘空间分析工具 v1.0                          ║
╚══════════════════════════════════════════════════════════╝

============================================================
  📦 Application Support (App 数据)
============================================================

       大小  应用
   --------------------------------------------------
        17G  DingTalkMac
       8.4G  XMind
       3.8G  com.apple.wallpaper
       1.8G  CodeBuddy CN
       1.5G  JetBrains
     ...

============================================================
  📋 清理建议
============================================================

   低风险清理:
   1. 缓存清理: rm -rf ~/Library/Caches/*
   2. Xcode 清理: rm -rf ~/Library/Developer/*
   3. Docker 清理: docker system prune -a
```

## 📁 常见空间杀手

| 应用 | 典型大小 | 说明 |
|------|----------|------|
| 钉钉 DingTalk | 10~30GB | 聊天记录本地数据库 |
| XMind | 5~10GB | 文件缓存 |
| JetBrains IDE | 2~5GB | 索引缓存 |
| Apple Aerial 壁纸 | 3~4GB | 动态壁纸视频 |
| Docker | 5~20GB | 镜像文件 |
| Xcode/模拟器 | 10~30GB | 开发工具 |

## 🔧 手动诊断命令

### 查看磁盘使用

```bash
# 磁盘总览
df -h

# Data 卷详情
df -h /System/Volumes/Data
```

### APFS 快照

```bash
# 列出快照
tmutil listlocalsnapshots /

# 删除快照（谨慎！）
tmutil deletelocalsnapshots /
```

### 查找大文件

```bash
# 查找 >500MB 的文件
find ~ -type f -size +500M -exec ls -lh {} \;

# 查找特定类型的文件
find ~ -name "*.dmg" -size +1G
```

### 应用缓存

```bash
# 查看 App Support 大目录
du -sh ~/Library/Application\ Support/* | sort -rh | head -20

# 查看缓存
du -sh ~/Library/Caches/* | sort -rh | head -15
```

## ⚠️ 清理注意事项

### ✅ 可以安全清理

- 用户缓存 (`~/Library/Caches/`)
- Xcode 派生数据 (`~/Library/Developer/`)
- Homebrew 旧版本 (`brew cleanup`)
- Docker 未使用镜像 (`docker image prune -a`)
- 浏览器缓存

### ⚠️ 谨慎清理

- 钉钉/微信聊天记录（可能无法恢复）
- 文档版本历史 (`.DocumentRevisions-V100`)
- Time Machine 本地备份

### ❌ 不要清理

- `/System/` 下的文件（SIP 保护）
- 数据库文件（`.db`）
- 不知道用途的文件

## 📝 License

MIT License - 可以自由使用、修改和分发

## 🤝 Contributing

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- GitHub: [duicym/macdisk-analyzer](https://github.com/duicym/macdisk-analyzer)
- Blog: [技术博客](https://blog.csdn.net/mwj_2014/article/details/161040899)
