#!/usr/bin/env python3
"""全量 IndexNow 分批提交：每批25个，间隔90秒，防风控。
用法：python3 indexnow_bulk_submit.py /tmp/all_urls.txt
"""
import json, sys, time, urllib.request, urllib.error

HOST = "www.aitoollab.top"
KEY = "b6a56baf28a44512b2d37748f5d6f3e4"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
API = "https://api.indexnow.org/IndexNow"
BATCH = 25
SLEEP = 90  # 秒

def submit_batch(batch):
    payload = json.dumps({
        "host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": batch
    }).encode("utf-8")
    req = urllib.request.Request(API, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:150]

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/all_urls.txt"
    with open(path) as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]
    print(f"共 {len(urls)} 个URL, 每批{BATCH}个, 间隔{SLEEP}s")
    ok, fail, skipped = 0, 0, 0
    for i in range(0, len(urls), BATCH):
        batch = urls[i:i+BATCH]
        status, err = submit_batch(batch)
        if status == 202:
            ok += len(batch)
            print(f"  ✅ 批{i//BATCH+1}: {len(batch)}个 成功 ({i+len(batch)}/{len(urls)})")
        elif status == 403 and "SiteVerification" in (err or ""):
            # 验证还没完成，等更久
            print(f"  ⏳ 批{i//BATCH+1}: 验证未完成, 等300s重试")
            time.sleep(300)
            status2, err2 = submit_batch(batch)
            if status2 == 202:
                ok += len(batch)
                print(f"  ✅ 重试成功: {len(batch)}个")
            else:
                fail += len(batch)
                print(f"  ❌ 重试仍失败: {status2} {err2}")
        elif status == 403 and "UserForbidded" in (err or ""):
            # 风控，等更久再继续
            print(f"  ⚠️ 风控触发, 等600s冷却")
            time.sleep(600)
            status2, err2 = submit_batch(batch)
            if status2 == 202:
                ok += len(batch)
                print(f"  ✅ 冷却后成功: {len(batch)}个")
            else:
                fail += len(batch)
                print(f"  ❌ 冷却后仍失败: {status2} {err2}")
        else:
            fail += len(batch)
            print(f"  ❌ 批{i//BATCH+1}: {status} {err}")
        if i + BATCH < len(urls):
            time.sleep(SLEEP)
    print(f"\n完成: 成功{ok} 失败{fail}")

if __name__ == "__main__":
    main()
