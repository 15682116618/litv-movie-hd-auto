#!/usr/bin/env python3
"""
update_hd_movie.py
------------------
自動抓取合法公開直播流，保存所有源，高清優先。
同時生成台灣、國際、全部三份總表，並自動推送到 GitHub。
"""

import os
import re
import requests
import subprocess
from datetime import datetime

# ====== 頻道分組 ======
CHANNEL_GROUPS = {
    "台灣頻道": {
        "龍華戲劇": "https://cdi.ofiii.com/ocean/video/playlist/UW147U4HPU4/litv-longturn21-avc1_336000=1-mp4a_140000=2.m3u8",
        "龍華電影": "https://cdi.ofiii.com/ocean/video/playlist/pKsJnCUdoTU/litv-longturn03-avc1_336000=1-mp4a_114000=2.m3u8"
    },
    "國際頻道": {
        "Al Jazeera English": "https://www.aljazeera.com/live/",
        "Bloomberg Global": "https://www.bloomberg.com/live/us"
    }
}

OUTPUT_DIR = "m3u-files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ====== 抓取串流 ======
def fetch_url(channel_name: str, url: str) -> list[str]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # 抓取所有 m3u8
        urls = re.findall(r"https://.+?\.m3u8", resp.text)
        if not urls:
            print(f"⚠️ {channel_name} 未檢測到任何串流")
            return []

        # 排序：高清優先
        def score(u):
            if "4000000" in u or "3000000" in u or "hd" in u or "high" in u:
                return 3
            if "2000000" in u or "2500000" in u:
                return 2
            return 1

        urls.sort(key=score, reverse=True)
        print(f"✅ {channel_name} 抓取到 {len(urls)} 個串流，高清優先")
        return urls

    except Exception as e:
        print(f"❌ 抓取 {channel_name} 出錯: {e}")
        return []

# ====== 更新所有頻道 ======
def update_all_channels():
    for group_name, channels in CHANNEL_GROUPS.items():
        group_dir = os.path.join(OUTPUT_DIR, group_name)
        os.makedirs(group_dir, exist_ok=True)

        for name, url in channels.items():
            urls = fetch_url(name, url)
            if not urls:
                continue

            path = os.path.join(group_dir, f"{name}.m3u")
            with open(path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for i, u in enumerate(urls):
                    tag = "高清優先" if i == 0 else "備用"
                    f.write(f"#EXTINF:-1 group-title=\"{group_name}\" tvg-name=\"{name}\",{name} ({tag})\n{u}\n")
                f.write(f"# 更新时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
            print(f"📄 已更新 {path}")

    generate_playlists()

# ====== 生成多總表 ======
def generate_playlists():
    lines_all = ["#EXTM3U\n"]
    lines_taiwan = ["#EXTM3U\n"]
    lines_international = ["#EXTM3U\n"]

    for group_name, channels in CHANNEL_GROUPS.items():
        group_dir = os.path.join(OUTPUT_DIR, group_name)
        if not os.path.exists(group_dir):
            continue
        for filename in os.listdir(group_dir):
            if filename.endswith(".m3u"):
                path = os.path.join(group_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    lines_all.append(content)
                    if group_name == "台灣頻道":
                        lines_taiwan.append(content)
                    elif group_name == "國際頻道":
                        lines_international.append(content)

    with open(os.path.join(OUTPUT_DIR, "taiwan.m3u"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines_taiwan))
    print("📄 已生成台灣頻道總表 taiwan.m3u")

    with open(os.path.join(OUTPUT_DIR, "international.m3u"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines_international))
    print("📄 已生成國際頻道總表 international.m3u")

    with open(os.path.join(OUTPUT_DIR, "all.m3u"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines_all))
    print("📄 已生成全部頻道總表 all.m3u")

# ====== Git 推送 ======
def push_to_github():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"🕒 Auto update {datetime.now():%Y-%m-%d %H:%M:%S}"], check=False)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=False)
        print("🚀 已自動推送到 GitHub")
    except Exception as e:
        print(f"⚠️ Git 推送失敗: {e}")

# ====== 主流程 ======
if __name__ == "__main__":
    update_all_channels()
    push_to_github()
