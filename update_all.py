#!/usr/bin/env python3
"""
update_hd_movie.py
------------------
示例脚本：定时抓取直播源页面，提取播放链接，生成 .m3u 文件。
在 fetch_url() 中放入你自己的抓取逻辑即可。
"""

import os
import re
import requests
from datetime import datetime

# ====== 频道配置 ======
CHANNELS = {
    "示例電影": "example-movie",   # 把这里换成你的频道名和标识
}

# ====== 抓取逻辑 ======
def fetch_url(channel_code: str) -> str | None:
    """
    自行修改这里的抓取逻辑：
      访问网页 -> 提取 .m3u8 地址 -> 返回字符串
    """
    try:
        url = f"https://example.com/channel/{channel_code}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # 替换下面正则为你目标站点的 .m3u8 地址匹配规则
        match = re.search(r"https://cdn\.example\.com/.+?\.m3u8", resp.text)
        return match.group(0) if match else None

    except Exception as e:
        print(f"⚠️ 抓取 {channel_code} 时出错: {e}")
        return None


# ====== 更新所有频道 ======
def update_all():
    os.makedirs("m3u-files", exist_ok=True)

    for name, code in CHANNELS.items():
        m3u_url = fetch_url(code)
        if not m3u_url:
            print(f"❌ {name} 未抓取到链接")
            continue

        content = f"""#EXTM3U
#EXTINF:-1 group-title="自定义频道",{name}
{m3u_url}
# 更新时间：{datetime.now():%Y-%m-%d %H:%M:%S}
"""
        path = f"m3u-files/{name}.m3u"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 已更新 {path}")

    generate_master_playlist(list(CHANNELS.keys()))


# ====== 汇总总表 ======
def generate_master_playlist(names: list[str]):
    base_url = "https://raw.githubusercontent.com/<你的用户名>/<仓库名>/main/m3u-files/"
    lines = ["#EXTM3U\n"]

    for n in names:
        lines.append(f"#EXTINF:-1 group-title='自定义频道',{n}")
        lines.append(f"{base_url}{n}.m3u\n")

    with open("m3u-files/all.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("📄 已生成总表 all.m3u")


if __name__ == "__main__":
    update_all()