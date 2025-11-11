#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動抓取台灣頻道直播流（龍華系列）
並保存至 m3u-files/all.m3u
"""

import os, time, subprocess, requests
from datetime import datetime
from seleniumwire import webdriver
import chromedriver_autoinstaller
from apscheduler.schedulers.background import BackgroundScheduler

# 頻道列表
CHANNELS = {
    "龍華戲劇": "https://www.ofiii.com/channel/watch/litv-longturn21",
    "龍華電影": "https://www.ofiii.com/channel/watch/litv-longturn03",
    "龍華偶像": "https://www.ofiii.com/channel/watch/litv-longturn12",
    "龍華經典": "https://www.ofiii.com/channel/watch/litv-longturn20"
}

OUTPUT_DIR = "m3u-files"
os.makedirs(OUTPUT_DIR, exist_ok=True)
chromedriver_autoinstaller.install()


def fetch_stream(channel_name, url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    print(f"[台灣頻道/{channel_name}] 🌍 正在加载页面...")
    time.sleep(20)

    streams = []
    for req in driver.requests:
        if req.response and ".m3u8" in req.url:
            if "avc1_" in req.url:
                streams.append(req.url)
    driver.quit()

    if streams:
        output_path = os.path.join(OUTPUT_DIR, f"{channel_name}.m3u")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for s in sorted(set(streams)):
                f.write(f"#EXTINF:-1 group-title=\"台灣頻道\" tvg-name=\"{channel_name}\",{channel_name}\n{s}\n")
            f.write(f"# 更新時間：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
        print(f"[{channel_name}] ✅ 抓取到 {len(streams)} 條流並保存")
    else:
        print(f"[{channel_name}] ⚠️ 沒有抓到任何流")


def update_all_channels():
    print(f"\n🕒 [{datetime.now():%Y-%m-%d %H:%M:%S}] 開始更新台灣頻道...")
    for name, url in CHANNELS.items():
        fetch_stream(name, url)
    merge_all()
    git_push()
    print("✅ 台灣頻道更新完成\n")


def merge_all():
    lines = ["#EXTM3U\n"]
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".m3u"):
            with open(os.path.join(OUTPUT_DIR, file), encoding="utf-8") as f:
                lines.append(f.read())
    all_path = os.path.join(OUTPUT_DIR, "all.m3u")
    with open(all_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("📄 已生成台灣頻道總表 all.m3u")


def git_push():
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", f"🕒 Auto update {datetime.now():%Y-%m-%d %H:%M:%S}"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=False)
    print("🚀 已自動推送到 GitHub")


# 主程序
scheduler = BackgroundScheduler()
scheduler.add_job(update_all_channels, 'interval', minutes=30)
scheduler.start()
update_all_channels()

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    scheduler.shutdown()
