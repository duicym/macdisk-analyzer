#!/usr/bin/env python3
"""
macOS 磁盘空间深度分析工具
Author: mawenjun
Date: 2026-05-12

无需 sudo 即可运行，输出结构化磁盘使用报告。
"""

import subprocess
import sys
import os
from datetime import datetime

# ANSI 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def run(cmd, timeout=60):
    """执行 shell 命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception as e:
        return f"ERROR: {e}", -1

def get_size(path):
    """获取目录大小"""
    out, _ = run(f"du -sh '{path}' 2>/dev/null")
    if out and '\t' in out:
        return out.split('\t')[0]
    return None

def parse_size(size_str):
    """将大小字符串转为 MB"""
    if not size_str:
        return 0
    try:
        if 'G' in size_str:
            return float(size_str.replace('G', '')) * 1024
        elif 'M' in size_str:
            return float(size_str.replace('M', ''))
        elif 'K' in size_str:
            return float(size_str.replace('K', '')) / 1024
        elif 'T' in size_str:
            return float(size_str.replace('T', '')) * 1024 * 1024
    except:
        pass
    return 0

def print_header(text):
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}  {text}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")

def print_subheader(text):
    print(f"{BOLD}{YELLOW}{text}{RESET}")

def check_apfs_snapshots():
    """检查 APFS 快照"""
    print_subheader("📸 APFS 快照")
    out, _ = run("tmutil listlocalsnapshots / 2>&1")
    lines = [l for l in out.split('\n') if 'com.apple.TimeMachine' in l or 'Snapshot' in l]
    if lines:
        print(f"{RED}⚠️  发现 {len(lines)} 个本地快照{RESET}")
        for line in lines[:5]:
            print(f"   {line}")
        if len(lines) > 5:
            print(f"   ... 共 {len(lines)} 个")
        print(f"\n   清理命令: {BOLD}tmutil deletelocalsnapshots /{RESET}")
    else:
        print(f"{GREEN}✅ 无本地快照{RESET}")

def check_disk_overview():
    """磁盘总览"""
    print_subheader("💾 磁盘总览")
    out, _ = run("df -h /System/Volumes/Data 2>/dev/null")
    for line in out.split('\n'):
        if '/dev/disk' in line or 'Filesystem' in line:
            print(f"   {line}")

    # APFS 卷信息
    out, _ = run("""diskutil apfs list 2>/dev/null | grep -A3 'Volume disk3s5'""")
    if out:
        print(f"\n   Data 卷详情:")
        for line in out.split('\n'):
            print(f"   {line}")

def check_user_dirs():
    """用户目录大小"""
    print_subheader("👤 用户目录")
    home = "/Users/mawenjun"
    if not os.path.exists(home):
        home = os.path.expanduser("~")

    out, _ = run(f"du -sh {home}/* 2>/dev/null | sort -rh | head -10")
    if out:
        print(f"   {'大小':>10}  目录")
        print(f"   {'-'*40}")
        for line in out.split('\n'):
            if '\t' in line:
                size, name = line.split('\t')
                print(f"   {size:>10}  {name}")

def check_app_support():
    """Application Support 分析"""
    print_subheader("📦 Application Support (App 数据)")

    home = "/Users/mawenjun"
    if not os.path.exists(home):
        home = os.path.expanduser("~")

    base = f"{home}/Library/Application Support"
    if not os.path.exists(base):
        print("   无法访问 Application Support 目录")
        return

    # 获取所有子目录
    out, _ = run(f"find '{base}' -maxdepth 1 -mindepth 1 -type d 2>/dev/null")
    if not out:
        print("   无子目录")
        return

    dirs = [d.strip() for d in out.split('\n') if d.strip()]
    results = []

    print(f"   {'大小':>10}  应用")
    print(f"   {'-'*50}")

    for d in dirs:
        name = d.split('/')[-1]
        size = get_size(d)
        if size and parse_size(size) > 0.1:  # > 100K
            results.append((name, size, parse_size(size)))
            if len(results) <= 30:
                print(f"   {size:>10}  {name[:40]}")

    results.sort(key=lambda x: x[2], reverse=True)

    total = get_size(base)
    print(f"\n   {'总计:':>10}  {total} ({len(results)} 个应用)")

    # 识别大户
    big_apps = [(n, s) for n, s, _ in results if parse_size(s) > 1024]  # > 1GB
    if big_apps:
        print(f"\n   {RED}🔥 空间大户 (>1GB):{RESET}")
        for name, size in big_apps:
            print(f"      {size:>10}  {name}")

def check_caches():
    """用户缓存分析"""
    print_subheader("🗃️  用户缓存 (Caches)")

    home = "/Users/mawenjun"
    if not os.path.exists(home):
        home = os.path.expanduser("~")

    base = f"{home}/Library/Caches"
    if not os.path.exists(base):
        print("   无法访问 Caches 目录")
        return

    out, _ = run(f"du -sh '{base}'/* 2>/dev/null | sort -rh | head -15")
    total = get_size(base)

    if out:
        print(f"   {'大小':>10}  缓存")
        print(f"   {'-'*50}")
        for line in out.split('\n'):
            if '\t' in line:
                size, name = line.split('\t')
                print(f"   {size:>10}  {name}")

        print(f"\n   {GREEN}✅ 缓存总计: {total} (可安全清理){RESET}")
        print(f"   清理命令: {BOLD}rm -rf ~/Library/Caches/*{RESET}")

def check_var_folders():
    """临时文件目录"""
    print_subheader("📁 /private/var/folders (临时文件)")
    size = get_size("/private/var/folders")
    if size:
        mb = parse_size(size)
        if mb > 1024:
            print(f"   {RED}⚠️  {size} - 较大，建议清理{RESET}")
        else:
            print(f"   {GREEN}✅ {size}{RESET}")

        out, _ = run("ls -la /private/var/folders/ 2>/dev/null")
        if out:
            lines = [l for l in out.split('\n') if 'd' in l and not 'total' in l]
            print(f"\n   子目录: {len(lines)} 个")
    else:
        print("   无法访问")

def check_docker():
    """Docker 镜像"""
    print_subheader("🐳 Docker")
    out, _ = run("docker system df 2>/dev/null")
    if out and "Images" in out:
        print(f"   {out}")
        out2, _ = run("docker images --format '{{.Repository}}\t{{.Size}}' 2>/dev/null | sort -k2 -rh | head -10")
        if out2:
            print(f"\n   镜像列表:")
            for line in out2.split('\n'):
                if '\t' in line:
                    repo, size = line.split('\t')
                    print(f"   {size:>10}  {repo[:40]}")
    else:
        print("   Docker 未安装或未运行")

def check_xcode():
    """Xcode/开发者工具"""
    print_subheader("🔧 Xcode/开发者工具")
    home = "/Users/mawenjun"
    if not os.path.exists(home):
        home = os.path.expanduser("~")

    paths = [
        (f"{home}/Library/Developer", "Developer"),
        (f"{home}/Library/Developer/CoreSimulator", "模拟器"),
    ]

    for path, name in paths:
        if os.path.exists(path):
            size = get_size(path)
            if size:
                mb = parse_size(size)
                if mb > 1024:
                    print(f"   {YELLOW}{size:>10}  {name}{RESET}")
                else:
                    print(f"   {size:>10}  {name}")

def check_homebrew():
    """Homebrew"""
    print_subheader("🍺 Homebrew")
    paths = [
        "/opt/homebrew/Cellar",
        "/usr/local/Cellar",
    ]

    total = 0
    for path in paths:
        if os.path.exists(path):
            size = get_size(path)
            if size:
                total += parse_size(size)
                mb = parse_size(size)
                if mb > 100:
                    print(f"   {size:>10}  {path}")

    if total > 0:
        print(f"\n   {GREEN}✅ Homebrew 总计: {total/1024:.1f}GB{RESET}")
    else:
        print("   Homebrew 未安装或路径不同")

def check_aerial_wallpaper():
    """Apple Aerial 动态壁纸"""
    print_subheader("🖼️ Apple Aerial 动态壁纸")

    home = "/Users/mawenjun"
    if not os.path.exists(home):
        home = os.path.expanduser("~")

    base = f"{home}/Library/Application Support/com.apple.wallpaper/aerials/videos"
    if not os.path.exists(base):
        print("   未使用 Aerial 壁纸")
        return

    out, _ = run(f"find '{base}' -type f 2>/dev/null")
    if not out:
        print("   无视频文件")
        return

    files = [f.strip() for f in out.split('\n') if f.strip()]
    total = 0
    for f in files:
        size = get_size(f)
        if size:
            total += parse_size(size)
            if parse_size(size) > 100:
                print(f"   {size:>10}  {f.split('/')[-1][:40]}")

    print(f"\n   {YELLOW}总计: {total/1024:.1f}GB ({len(files)} 个视频){RESET}")
    print(f"   清理: 系统设置 → 壁纸 → 选择静态图片")

def check_jetbrains():
    """JetBrains IDE 缓存"""
    print_subheader("💡 JetBrains IDE")

    home = "/Users/mawenjun"
    if not os.path.exists(home):
        home = os.path.expanduser("~")

    paths = [
        (f"{home}/Library/Caches/JetBrains", "缓存"),
        (f"{home}/Library/Application Support/JetBrains", "配置"),
    ]

    total = 0
    for path, name in paths:
        if os.path.exists(path):
            size = get_size(path)
            if size:
                total += parse_size(size)
                mb = parse_size(size)
                if mb > 100:
                    print(f"   {size:>10}  {name}")

    if total > 0:
        print(f"\n   {GREEN}✅ JetBrains 总计: {total/1024:.1f}GB{RESET}")
        print(f"   清理: IDE → File → Invalidate Caches")

def main():
    print(f"\n{BLUE}{BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     macOS 磁盘空间分析工具 v1.0                          ║")
    print("║     Author: mawenjun | Date: 2026-05-12                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    check_disk_overview()
    check_apfs_snapshots()
    check_user_dirs()
    check_app_support()
    check_caches()
    check_aerial_wallpaper()
    check_jetbrains()
    check_xcode()
    check_homebrew()
    check_docker()
    check_var_folders()

    print_header("📋 清理建议")
    print("""
   低风险清理（可立即执行）:
   ┌─────────────────────────────────────────────────────────┐
   │  1. 缓存清理:      rm -rf ~/Library/Caches/*           │
   │  2. Xcode 清理:    rm -rf ~/Library/Developer/*        │
   │  3. Homebrew 清理: brew cleanup                         │
   │  4. Docker 清理:   docker system prune -a              │
   └─────────────────────────────────────────────────────────┘

   中风险清理（确认后执行）:
   ┌─────────────────────────────────────────────────────────┐
   │  1. 钉钉缓存:      钉钉设置 → 清除缓存                  │
   │  2. XMind 缓存:    删除 ~/Library/Application Support/  │
   │                    XMind/Electron v3/vana/file-cache/   │
   │  3. 快照清理:      tmutil deletelocalsnapshots /       │
   └─────────────────────────────────────────────────────────┘

   高风险清理（不建议手动）:
   ┌─────────────────────────────────────────────────────────┐
   │  1. System 卷下的文件 (受 SIP 保护)                     │
   │  2. 文档版本历史 (.DocumentRevisions-V100)             │
   │  3. Time Machine 本地备份 (.MobileBackups)             │
   └─────────────────────────────────────────────────────────┘
""")

    print(f"\n{GREEN}✅ 分析完成！{RESET}\n")

if __name__ == "__main__":
    main()
