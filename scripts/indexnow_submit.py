#!/usr/bin/env python3
"""IndexNow 自动提交：新文章发布后立即通知 Bing/Yandex/Naver 收录。

用法：
  python3 indexnow_submit.py                # 提交 sitemap.xml 里所有 URL
  python3 indexnow_submit.py /path/urls.txt # 提交指定文件里的 URL（每行一个）
"""
import json, sys, urllib.request, urllib.error

HOST = "www.aitoollab.top"
KEYS = ["b6a56baf28a44512b2d37748f5d6f3e4", "4a7cdecf71d74733a36e72e2fd034608"]
KEY = KEYS[0]  # 默认用第一个，失败时轮换
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
                # IndexNow 定位：新文章即时通知。默认只提交最新 5 个URL（风控友好）
                return urls[-5:]
    # 回退：远程 sitemap
    try:
        with urllib.request.urlopen(f"https://{HOST}/sitemap.xml", timeout=30) as r:
            xml = r.read().decode("utf-8")
        return re.findall(r"<loc>(.*?)</loc>", xml)[-5:]
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
        success = False
        # 多 key 轮换：一个失败换下一个
        for key in KEYS:
            key_loc = f"https://{HOST}/{key}.txt"
            payload = json.dumps({
                "host": HOST,
                "key": key,
                "keyLocation": key_loc,
                "urlList": batch,
            }).encode("utf-8")
            req = urllib.request.Request(API, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    ok += len(batch)
                    success = True
                    break
            except urllib.error.HTTPError as e:
                body = e.read().decode()[:100]
                if e.code == 403 and "UserForbidded" in body:
                    continue  # 换下一个 key
                fail += len(batch)
                print(f"[ERR] IndexNow {e.code}: {body}")
                break
        if not success and fail == 0:
            fail += len(batch)
    print(f"[OK] IndexNow: 提交 {ok} 个URL成功, {fail} 个失败")
    return ok > 0


if __name__ == "__main__":
    urls = get_urls()
    submit(urls)
