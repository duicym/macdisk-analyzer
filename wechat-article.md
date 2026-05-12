# 新 Mac「系统数据」占了几十 GB？用这个工具精准诊断

## 📌 写在前面

五一假期给新 Mac 做了系统迁移，结果发现「系统数据」占了 **60GB**——一个全新的 Mac，系统数据怎么会这么大？

试了 DaisyDisk、CleanMyMac 等工具，要么收费，要么扫出来都是 App 缓存这种小头，真正的大户根本找不到。

最后逼得没办法，自己写了工具深度扫描，才把真实原因揪出来。

---

## 🔍「系统数据」到底包含了什么？

macOS 的「系统数据」是个筐，包含以下几类：

| 类别 | 典型大小 | 说明 |
|------|----------|------|
| **App 数据和缓存** | 10~100GB | Application Support 目录 |
| **沙盒临时文件** | 1~10GB | /private/var/folders |
| **APFS 快照** | 0~50GB | Time Machine 本地备份 |
| **文档版本历史** | 0~20GB | .DocumentRevisions-V100 |
| **日志文件** | 0~5GB | /var/log |

**普通清理工具扫不出来**，因为它们大部分不会递归扫描 Application Support 里的 App 数据库文件。

---

## 🚀 我写了一个诊断工具

今天把这个分析工具开源了，支持：

- ✅ 无需 sudo，普通用户权限即可运行
- ✅ Apple Silicon + Intel Mac 兼容
- ✅ 精准定位 Application Support 里的大文件
- ✅ 识别 APFS 快照、缓存、临时文件
- ✅ 给出低/中/高风险清理建议

### 一键运行

```bash
python3 https://raw.githubusercontent.com/mawenjun/macdisk-analyzer/main/scripts/analyze.py
```

### 效果示例

```
============================================================
  📦 Application Support (App 数据)
============================================================

       大小  应用
   --------------------------------------------------
        17G  DingTalkMac           ← 钉钉聊天数据库
       8.4G  XMind                 ← XMind 文件缓存
       3.8G  com.apple.wallpaper   ← 动态壁纸视频
       1.8G  CodeBuddy CN
       1.5G  JetBrains
     ...

============================================================
  🗃️  用户缓存 (Caches)
============================================================

       大小  缓存
   --------------------------------------------------
       5.5G  ~/Library/Caches     ← 可安全清理

============================================================
  📋 清理建议
============================================================

   ✅ 低风险清理:
   ┌─────────────────────────────────────────────────┐
   │  1. 缓存清理: rm -rf ~/Library/Caches/*        │
   │  2. Xcode 清理: rm -rf ~/Library/Developer/*  │
   │  3. Docker 清理: docker system prune -a        │
   └─────────────────────────────────────────────────┘

   ⚠️ 中风险清理:
   ┌─────────────────────────────────────────────────┐
   │  1. 钉钉缓存: 钉钉设置 → 清除缓存              │
   │  2. XMind 缓存: 删除 XMind/file-cache/         │
   └─────────────────────────────────────────────────┘
```

---

## 💡 我的诊断结果（附清理方案）

跑完分析后，我发现新 Mac「系统数据」60GB 的构成如下：

### 🏆 空间大户 Top 5

| 排名 | 应用 | 大小 | 详情 | 清理方式 |
|------|------|------|------|----------|
| 🥇 | **钉钉** | **17GB** | `dingtalk.db` 聊天记录数据库 | 钉钉设置 → 清除缓存 |
| 🥈 | **XMind** | **8.4GB** | `file-cache/` 里几百个 XMind 文件缓存 | 删除缓存目录 |
| 🥉 | **Apple Aerial 壁纸** | **3.8GB** | 7 个动态壁纸视频（每段 ~300MB~1.3GB） | 换壁纸为静态图片 |
| 4 | CodeBuddy CN | 1.8GB | AI 代码助手缓存 | 设置里清除 |
| 5 | JetBrains | 1.5GB | IDEA 索引 + 插件 | IDE 内 `Invalidate Caches` |

### 📊 全部分布

```
Application Support:  46GB  ← App 数据
用户缓存:              5.5GB  ← 可安全清理
var/folders:          10GB  ← 临时文件
Docker Images:         4.1GB  ← 可回收 1.75GB
---
总计:                  ~65GB
```

---

## 🧹 我的清理方案

清理完成后，「系统数据」从 **60GB → 35GB**，释放了 **25GB**。

### 清理步骤

**1. 清理缓存（安全，无风险）**
```bash
rm -rf ~/Library/Caches/*
```

**2. 清理 XMind 缓存（安全）**
```bash
rm -rf ~/Library/Application\ Support/XMind/Electron\ v3/vana/file-cache/
```

**3. 清理 Apple Aerial 壁纸（安全）**
```
系统设置 → 壁纸 → 选择静态图片（推荐「干净」）
```

**4. 钉钉缓存（中等风险）**
```
钉钉 → 设置 → 通用 → 清除缓存
```
⚠️ 会清除本地聊天记录缓存，重新登录后会重新下载。如果钉钉聊天记录云端有备份，可以放心清。

**5. 清理 Docker 未使用镜像**
```bash
docker image prune -a
```

**6. Xcode 派生数据（安全，需要时会重建）**
```bash
rm -rf ~/Library/Developer/*
```

---

## ⚠️ 这些不要乱删

| 目录/文件 | 为什么不能删 |
|-----------|--------------|
| `/System/` | SIP 保护，删了系统崩溃 |
| `.DocumentRevisions-V100` | 文档版本历史，可能有重要版本 |
| `.db` 数据库文件 | 可能是 App 的核心数据 |
| `~/Library/Containers/` | macOS App Sandbox 数据，乱删可能丢数据 |

---

## 📦 工具开源地址

GitHub: **[github.com/mawenjun/macdisk-analyzer](https://github.com/mawenjun/macdisk-analyzer)**

包含：
- `analyze.py` - 主分析脚本
- `SKILL.md` - 详细技能文档
- `README.md` - 使用说明

如果你也遇到「系统数据」占用过大的问题，欢迎试试这个工具，有问题可以在 GitHub 提 Issue。

---

## 💬 总结

「系统数据」大不是玄学，基本都是：
1. **聊天软件数据库**（钉钉/微信/QQ）
2. **办公软件缓存**（XMind/Office）
3. **IDE 索引**（JetBrains/XCode）
4. **壁纸/主题资源**（Aerial 视频/主题包）
5. **Time Machine 快照**

用工具扫一遍，就能精准定位，清理起来心里也有底。

---

*你被「系统数据」坑过吗？欢迎在评论区分享你的经历。*

---

### 🔗 相关阅读

- [macOS 清理指南：释放空间的正确姿势](https://example.com)
- [Apple Silicon Mac 迁移指南](https://example.com)
- [GitHub: macdisk-analyzer](https://github.com/mawenjun/macdisk-analyzer)
