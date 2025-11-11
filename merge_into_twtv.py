#!/usr/bin/env python3
"""
merge_into_twtv.py
------------------
僅更新 TWTV.m3u 中「台灣頻道」區塊，不影響其他頻道。
"""

import os
import re
import requests
from datetime import datetime

# === 基本設定 ===
GITHUB_TWTV_RAW_URL = "https://raw.githubusercontent.com/15682116618/ML-MO-GOT-IPTV/main/TWTV.m3u"
LOCAL_TWTV_PATH = "TWTV.m3u"
SOURCE_DIR = "m3u-files"

def download_twtv():
    """從 GitHub 下載最新 TWTV.m3u"""
    print("🌐 正在下載遠程 TWTV.m3u ...")
    r = requests.get(GITHUB_TWTV_RAW_URL, timeout=15)
    if r.status_code == 200:
        with open(LOCAL_TWTV_PATH, "w", encoding="utf-8") as f:
            f.write(r.text)
        print("✅ 已下載最新 TWTV.m3u")
    else:
        raise RuntimeError(f"❌ 無法下載 TWTV.m3u（HTTP {r.status_code}）")

def collect_taiwan_streams():
    """從 m3u-files 讀取所有台灣頻道串流"""
    lines = ["#EXTM3U\n"]
    for file in os.listdir(SOURCE_DIR):
        if file.endswith(".m3u"):
            path = os.path.join(SOURCE_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if data and "#EXTINF" in data:
                    lines.append(data)
    lines.append(f"# 更新時間：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
    return "\n".join(lines)

def replace_taiwan_section(original_text, new_taiwan_text):
    """
    在 TWTV.m3u 文字中，用 new_taiwan_text 替換原本「台灣頻道」區塊
    """
    # 找出台灣區塊的開始和結束
    pattern = re.compile(
        r'(#EXTINF:-1.*?group-title="台灣頻道".*?http[^\n]+)+',
        re.DOTALL
    )

    if not re.search(pattern, original_text):
        print("⚠️ 未找到台灣頻道區塊，將在檔尾新增。")
        return original_text.strip() + "\n\n" + new_taiwan_text

    new_text = re.sub(pattern, new_taiwan_text.strip(), original_text)
    return new_text

def merge_sources():
    """執行整合更新"""
    # 1️⃣ 下載最新 TWTV.m3u
    download_twtv()

    # 2️⃣ 讀取原檔
    with open(LOCAL_TWTV_PATH, "r", encoding="utf-8") as f:
        original = f.read()

    # 3️⃣ 收集新抓取的台灣頻道流
    taiwan_section = collect_taiwan_streams()

    # 4️⃣ 替換台灣區段
    merged = replace_taiwan_section(original, taiwan_section)

    # 5️⃣ 覆蓋 TWTV.m3u
    with open(LOCAL_TWTV_PATH, "w", encoding="utf-8") as f:
        f.write(merged)
    print("✅ 已更新 TWTV.m3u 中的台灣頻道區塊")

def git_push():
    """提交更新到 GitHub"""
    print("🚀 正在推送到 GitHub ...")
    os.system("git add TWTV.m3u")
    os.system(f'git commit -m "🕒 Auto merge 台灣頻道 {datetime.now():%Y-%m-%d %H:%M:%S}"')
    os.system("git push origin main")

if __name__ == "__main__":
    merge_sources()
    git_push()
