#!/usr/bin/env python3
"""SEO优化闭环检测——对比新关键词报告 vs 基线，判断优化是否正向。

用法：python3 seo_tracking_check.py /path/to/new_keyword_report.csv
输出：每个追踪词的变化（排名↑/↓）+ 整体结论（方向对/需要调整）
"""
import csv, json, os, sys

TRACKING = "/home/agentuser/.hermes/data/seo_tracking.json"

def load_new_report(path):
    rows = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.reader(f):
            if len(r) >= 5 and r[1].strip().isdigit():
                rows[r[0]] = {"imp": int(r[1]), "clicks": int(r[2]), "rank": float(r[4])}
    return rows

def main():
    new_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not new_path:
        print("用法: python3 seo_tracking_check.py /path/to/new_keyword_report.csv")
        return
    with open(TRACKING) as f:
        tracking = json.load(f)
    new = load_new_report(new_path)

    print(f"=== SEO闭环检测 ({tracking['baseline_date']} vs 新报告) ===\n")
    improved, worsened, missing = [], [], []
    for k in tracking["keywords"]:
        kw = k["keyword"]
        old_rank = k["rank"]
        old_imp = k["impressions"]
        if kw in new:
            new_rank = new[kw]["rank"]
            new_imp = new[kw]["imp"]
            rank_delta = old_rank - new_rank  # 正=排名上升
            imp_delta = new_imp - old_imp    # 正=印象增加
            verdict = "✅ 正向" if (rank_delta > 0.5 or imp_delta > 5) else ("❌ 负向" if (rank_delta < -0.5 and imp_delta < -3) else "➡️ 持平")
            if verdict == "✅ 正向":
                improved.append(kw)
            elif verdict == "❌ 负向":
                worsened.append(kw)
            else:
                missing.append(kw)  # 持平也算在观察
            print(f"  {kw[:30]:<32} 排名 {old_rank:.1f}→{new_rank:.1f} ({'+' if rank_delta>0 else ''}{rank_delta:.1f}) | 印象 {old_imp}→{new_imp} {verdict}")
        else:
            print(f"  {kw[:30]:<32} 新报告中未出现（可能无印象了）")
            missing.append(kw)

    # 流量对比
    cf_path = "/home/agentuser/.hermes/data/cf_analytics_history.json"
    if os.path.exists(cf_path):
        try:
            with open(cf_path) as f:
                cf = json.load(f)
            # 取最近几天的 uniques
            hist = cf if isinstance(cf, list) else cf.get("history", [])
            if hist:
                recent = hist[-7:]
                avg = sum(float(h.get("uniques", 0)) for h in recent) / len(recent)
                print(f"\n📊 最近7天平均真实访客: {avg:.0f}/天 (基线: 400-570)")
                print(f"    {'✅ 在基线内' if 400 <= avg <= 570 else ('⬆️ 超基线（正向）' if avg > 570 else '⬇️ 低于基线（需关注）')}")
        except Exception as e:
            print(f"\n📊 流量读取失败: {e}")

    print(f"\n=== 结论 ===")
    if improved:
        print(f"✅ 优化生效: {len(improved)}个词正向 ({', '.join(improved[:5])})")
    if worsened:
        print(f"❌ 需要调整: {len(worsened)}个词负向 ({', '.join(worsened[:5])})")
    if not improved and not worsened:
        print("➡️ 全部持平：优化尚在生效期（通常需要1-4周），继续观察")
    if improved and not worsened:
        print("🎯 方向正确，继续保持+扩大优化范围")
    if worsened:
        print("🔧 方向部分有误，需要针对负向词调整策略（改内容/改标题/换词）")

if __name__ == "__main__":
    main()
