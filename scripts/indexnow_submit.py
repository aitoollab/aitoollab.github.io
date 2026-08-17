#!/usr/bin/env python3
"""IndexNow 自动提交：新文章发布后立即通知 Bing/Yandex/Naver 收录。

用法：
  python3 indexnow_submit.py                # 提交 sitemap.xml 里所有 URL
  python3 indexnow_submit.py /path/urls.txt # 提交指定文件里的 URL（每行一个）
"""
import json, sys, urllib.request, urllib.error

HOST = "www.aitoollab.top"
KEY = "d0bfd875af5f46e48db4f0d38ccfa22e"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
API = "https://api.indexnow.org/IndexNow"


def get_urls():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            return [l.strip() for l in f if l.strip().startswith("http")]
    # 优先读本地 sitemap.xml（脚本位于仓库 scripts/ 下）
    import os, re
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for candidate in [os.path.join(repo, "sitemap.xml")]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                return re.findall(r"<loc>(.*?)</loc>", f.read())[:500]
    # 回退：远程 sitemap
    try:
        with urllib.request.urlopen(f"https://{HOST}/sitemap.xml", timeout=30) as r:
            xml = r.read().decode("utf-8")
        return re.findall(r"<loc>(.*?)</loc>", xml)[:500]
    except Exception as e:
        print(f"[ERR] 读取sitemap失败: {e}")
        return []


def submit(urls):
    if not urls:
        print("[SKIP] 无URL可提交")
        return
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(API, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"[OK] IndexNow {r.status}: 提交 {len(urls)} 个URL")
            return True
    except urllib.error.HTTPError as e:
        print(f"[ERR] IndexNow {e.code}: {e.read().decode()[:200]}")
        return False


if __name__ == "__main__":
    urls = get_urls()
    submit(urls)
