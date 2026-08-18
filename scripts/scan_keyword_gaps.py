#!/usr/bin/env python3
"""存量页面关键词体检——找出"有印象但排名>5"的搜索词，匹配到对应页面。

用法：python3 scan_keyword_gaps.py /path/to/keyword_report.csv
输出：缺口清单（词→匹配页面→建议动作）
"""
import csv, os, re, sys

REPO = "/home/agentuser/.hermes/hermes-agent/aitoollab"

def load_keywords(csv_path):
    """读关键词报告，返回 [(kw, imp, clicks, ctr, rank)]"""
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for r in csv.reader(f):
            if len(r) >= 5 and r[1].strip().isdigit():
                rows.append((r[0], int(r[1]), int(r[2]), float(r[3].replace('%','')), float(r[4])))
    return rows

def find_page_for_keyword(kw, index):
    """找最匹配的页面：标题/h1 包含关键词核心词"""
    # 提取关键词核心（去掉修饰词）
    core = kw
    # 在索引里找包含关键词的页面
    best, best_score = None, 0
    kw_chars = set(kw.replace(" ", ""))
    for path, title in index.items():
        t = title.replace(" - AiToollab", "").replace("｜AiToollab", "")
        # 精确包含
        if kw in t or kw in path:
            return path, "精确匹配"
        # 核心词包含（去掉"怎么/如何/赚钱/副业"等泛词后）
        core_kw = re.sub(r"[怎么如何赚钱副业变现收入月入教程攻略方法]" , "", kw)
        if len(core_kw) >= 3 and core_kw in t:
            return path, "核心词匹配"
        # 字符重叠度
        t_chars = set(t.replace(" ", ""))
        overlap = len(kw_chars & t_chars) / max(len(kw_chars), 1)
        if overlap > best_score:
            best_score = overlap
            best = path
    if best and best_score > 0.5:
        return best, f"模糊匹配({best_score:.0%})"
    return None, None

def build_index():
    """建立 slug→title 索引"""
    index = {}
    for root, dirs, files in os.walk(REPO):
        if "index.html" in files and ("articles" in root or "tutorials" in root):
            f = os.path.join(root, "index.html")
            try:
                c = open(f, encoding="utf-8").read()
                m = re.search(r"<title>(.*?)</title>", c, flags=re.S)
                title = m.group(1).strip() if m else ""
                path = os.path.relpath(f, REPO).replace("/index.html", "")
                index[path] = title
            except Exception:
                pass
    return index

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not csv_path:
        print("用法: python3 scan_keyword_gaps.py /path/to/keyword_report.csv")
        return
    rows = load_keywords(csv_path)
    index = build_index()
    print(f"关键词总数: {len(rows)}, 页面索引: {len(index)}\n")

    # 机会词：印象≥10 且 排名>5
    gaps = [r for r in rows if r[1] >= 10 and r[4] > 5]
    gaps.sort(key=lambda x: -x[1])
    print("=== 机会词清单（印象≥10 且 排名>5）===")
    for kw, imp, clicks, ctr, rank in gaps:
        path, match = find_page_for_keyword(kw, index)
        status = f"→ {path} ({match})" if path else "→ ❌ 无匹配页面"
        print(f"  {kw[:40]} | 印象{imp} 排名{rank:.1f} {status}")

    # 已覆盖但排名差的：印象≥10 且 排名>5 且 有匹配页面
    print("\n=== 已覆盖但排名差（需要补强内容）===")
    covered = [(kw, imp, clicks, ctr, rank, path, match) for kw, imp, clicks, ctr, rank in gaps
               if (path := find_page_for_keyword(kw, index)[0])]
    for kw, imp, clicks, ctr, rank, path, match in sorted(covered, key=lambda x: -x[1])[:10]:
        print(f"  {kw[:35]} | 印象{imp} 排名{rank:.1f} → {path}")

if __name__ == "__main__":
    main()
