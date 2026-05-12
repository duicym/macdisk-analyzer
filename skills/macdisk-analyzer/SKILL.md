---
name: macdisk-analyzer
description: macOS 磁盘空间深度分析工具。精准定位系统数据占用来源，识别大文件、缓存、旧快照等空间杀手。支持 Apple Silicon 和 Intel Mac，提供结构化分析报告和清理建议。
author: mawenjun
version: "1.0"
tags: [macOS, disk, storage, analysis, cleanup]
created: 2026-05-12
agent_created: true
---

# macdisk-analyzer

> macOS 磁盘空间深度分析工具 — 精准定位"系统数据"占用源头

## 功能概述

通过 Python + Shell 脚本深度扫描 macOS 磁盘使用情况，识别：
- **系统数据（System Data）** 大户：钉钉/XMind/IDE 缓存/数据库
- **APFS 快照**：Time Machine 本地备份残留
- **缓存目录**：跨应用的缓存堆积
- **临时文件**：沙盒/var/folders 等临时存储
- **大型文件**：递归定位 >100MB 的文件

## 适用场景

- macOS「系统数据」占用异常大（数十 GB）
- 磁盘空间告急，需要精准清理
- 新 Mac 迁移后空间异常
- 不想装第三方清理工具，想自己诊断

## 使用方式

### 方式一：运行完整分析脚本（推荐）

```bash
python3 ~/github/macdisk-analyzer/scripts/analyze.py
```

脚本会自动：
1. 检查 APFS 快照数量
2. 扫描 Data 卷各目录大小
3. 列出 Application Support 前 20 大应用
4. 检查用户缓存（Caches）
5. 检查 /private/var/folders
6. 检查 Docker Images
7. 输出汇总表格

### 方式二：分步诊断

```bash
# 1. 检查快照
tmutil listlocalsnapshots /

# 2. 查看 Data 卷总览
df -h /System/Volumes/Data

# 3. 列出用户目录大小排行
du -sh /Users/*

# 4. 列出 Application Support 大目录
du -sh ~/Library/Application\ Support/* | sort -rh | head -20

# 5. 查看缓存
du -sh ~/Library/Caches/* | sort -rh | head -15

# 6. 检查 Homebrew
du -sh /opt/homebrew/Cellar/*
```

### 方式三：深度诊断（需要 sudo）

```bash
# 检查系统日志
sudo du -sh /var/log

# 检查临时文件目录
sudo du -sh /private/var/folders

# 查看 Docker 镜像
docker images
docker system df
```

## 关键目录速查表

| 目录 | 典型大小 | 含义 | 可清理？ |
|---|---|---|---|
| `~/Library/Application Support/` | 10~100G | App 数据和缓存 | ⚠️ 部分可清 |
| `~/Library/Caches/` | 1~10G | 系统缓存 | ✅ 安全 |
| `~/Library/Containers/` | 5~20G | macOS App Sandbox 数据 | ⚠️ 谨慎 |
| `/private/var/folders` | 1~10G | 临时文件 | ✅ 安全 |
| `~/Library/Developer/` | 1~10G | Xcode/模拟器 | ✅ 安全 |
| `/opt/homebrew/Cellar/` | 1~10G | Homebrew 包 | ✅ 安全 |
| `.MobileBackups` | 0~100G | Time Machine 本地备份 | ⚠️ 需要 TM |
| `.DocumentRevisions-V100` | 0~50G | 文档版本历史 | ⚠️ 可能重要 |

## 常见「系统数据」大户

### 1. 钉钉 DingTalk
```
~/Library/Application Support/DingTalkMac/
├── 23576626_v2/DBFiles/dingtalk.db      # 聊天记录数据库
└── globalStorage/                         # 缓存
```
- **清理方式**：钉钉设置 → 清除缓存（会重新下载聊天记录）

### 2. XMind
```
~/Library/Application Support/XMind/
├── vana/file-cache/                       # XMind 文件缓存
└── auto-updater/                          # 更新包残留
```
- **清理方式**：在 XMind 内清除缓存，或手动删除 `file-cache/`

### 3. JetBrains IDE
```
~/Library/Caches/JetBrains/                 # 索引缓存
~/Library/Application Support/JetterBrains/ # 配置和缓存
```
- **清理方式**：IDE 内 `File → Invalidate Caches`

### 4. Apple Aerial 动态壁纸视频
```
~/Library/Application Support/com.apple.wallpaper/aerials/videos/
```
- **大小**：7 个视频约 3~4GB
- **清理方式**：系统设置 → 更换壁纸为静态图片

### 5. Docker
```
docker system df                            # 查看空间占用
docker image prune -a                       # 清理未使用镜像
```

## 核心脚本说明

### `scripts/analyze.py`

主分析脚本，无需 sudo 即可运行。输出包括：
- APFS 快照统计
- Data 卷目录大小排行
- Application Support Top 20
- 用户缓存统计
- var/folders 大小
- Docker 镜像统计

### `scripts/deep_scan.py`

深度扫描脚本（需要 sudo）：
- 系统日志大小
- /private/var/folders 详细
- APFS 快照详情

## 注意事项

1. **删除前确认**：大文件（>1GB）删除前务必确认用途
2. **数据库文件**：`.db` 文件可能是重要数据，不要随意删除
3. **Time Machine**：确认不再需要本地快照后再删除 `.MobileBackups`
4. **SIP 保护文件**：`/System` 下大部分文件受 SIP 保护，不可随意修改
5. **Homebrew**：清理 Cellar 前确认不再需要旧版本包

## 技术背景

- **Apple Silicon Mac**：用户目录在 `/System/Volumes/Data/Users/`
- **APFS 分区**：macOS 10.13+ 使用 APFS，支持快照和克隆
- **System Data**：「系统数据」类别包含所有非用户文件的系统占用
- **purgeable 空间**：系统可自动回收的已删除但未释放空间

## 更新日志

- **v1.0** (2026-05-12)：初始版本，支持完整磁盘分析
