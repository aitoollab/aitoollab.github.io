#!/usr/bin/env python3
"""IndexNow 自动提交：新文章发布后立即通知 Bing/Yandex/Naver 收录。

用法：
  python3 indexnow_submit.py                # 提交 sitemap.xml 里所有 URL
  python3 indexnow_submit.py /path/urls.txt # 提交指定文件里的 URL（每行一个）
"""
import json, sys, urllib.request, urllib.error

HOST = "www.aitoollab.top"
KEY = "7af5801d3868400c8fad0a949cebd385"
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
                urls = re.findall(r"<loc>(.*?)</loc>", f.read())
                # IndexNow 定位：新文章即时通知。每次只提交最新 2 个URL（少推送，防风控）
                return urls[-2:]
    # 回退：远程 sitemap
    try:
        with urllib.request.urlopen(f"https://{HOST}/sitemap.xml", timeout=30) as r:
            xml = r.read().decode("utf-8")
        return re.findall(r"<loc>(.*?)</loc>", xml)[-2:]
    except Exception as e:
        print(f"[ERR] 读取sitemap失败: {e}")
        return []


def submit(urls):
    if not urls:
        print("[SKIP] 无URL可提交")
        return
    # IndexNow 单次提交限制：分批，每批≤25个
    batch_size = 25
    ok, fail = 0, 0
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        payload = json.dumps({
            "host": HOST,
            "key": KEY,
            "keyLocation": KEY_LOCATION,
            "urlList": batch,
        }).encode("utf-8")
        req = urllib.request.Request(API, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                ok += len(batch)
        except urllib.error.HTTPError as e:
            fail += len(batch)
            body = e.read().decode()[:100]
            if fail and i == 0:
                print(f"[ERR] IndexNow {e.code}: {body}")
    print(f"[OK] IndexNow: 提交 {ok} 个URL成功, {fail} 个失败")
    return ok > 0


if __name__ == "__main__":
    urls = get_urls()
    submit(urls)
