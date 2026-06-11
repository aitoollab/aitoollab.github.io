#!/opt/scrapling-api/venv/bin/python3
"""
Scout Scrapling 引擎
让 Scout 的发现从"拉README"升级为深度分析
"""
import json
import os
import sys
from datetime import datetime

STATE_FILE = "/home/agentuser/.hermes/hermes-agent/aitoollab/.scout-state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"discovered": {}, "researched": [], "projects": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def enrich_project(item):
    """用 Scrapling 深度分析一个项目"""
    import subprocess
    
    url = item.get("url", "")
    name = item.get("name", "") or item.get("repo", "")
    
    print(f"  分析: {name}")
    
    # 抓取 GitHub README 完整内容
    owner_repo = name
    readme_url = f"https://raw.githubusercontent.com/{owner_repo}/main/README.md"
    
    # 跳过非 GitHub repo 格式的项目（如 HN stories）
    if "/" not in owner_repo or " " in owner_repo or owner_repo == "?":
        item["enriched"] = True
        item["analysis"] = {
            "installable": False,
            "has_api": False,
            "has_pricing": False,
            "has_docs": False,
            "has_examples": False,
            "readme_length": 0,
            "readme_sections": 0
        }
        item["readme_full"] = ""
        return item
    
    try:
        import urllib.request
        req = urllib.request.Request(readme_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            readme = resp.read().decode("utf-8", errors="ignore")[:10000]
    except:
        readme = ""
    
    # 分析 README 中的关键信息
    analysis = {
        "has_installation": "pip install" in readme or "npm install" in readme or "git clone" in readme,
        "has_api": "api" in readme.lower() or "endpoint" in readme.lower(),
        "has_pricing": "$" in readme or "pricing" in readme.lower() or "paid" in readme.lower(),
        "has_docs": "docs" in readme.lower() or "documentation" in readme.lower(),
        "has_examples": "example" in readme.lower() or "usage" in readme.lower(),
        "readme_length": len(readme),
        "analyzed_at": datetime.now().isoformat()
    }
    
    # 更新状态
    item["enriched"] = True
    item["analysis"] = analysis
    item["readme_full"] = readme[:5000]
    
    score = item.get("research_score", 0)
    if analysis["has_installation"]:
        score += 5
    if analysis["has_examples"]:
        score += 5
    if analysis["has_pricing"]:
        score += 10  # 有定价=变现潜力高
    if analysis["has_api"]:
        score += 5
    item["research_score"] = min(score, 100)
    
    return item

def main():
    print("=== Scout 深度分析引擎 ===\n")
    
    state = load_state()
    
    # 从 latest_enrichment 获取本次待分析项目（由外部 scout 传入）
    # 或从 top_candidates 中查找未深度分析的
    candidates = []
    already_enriched_repos = set()
    for item in state.get("latest_enrichment", []):
        already_enriched_repos.add(item.get("repo", ""))
    
    for item in state.get("top_candidates", []):
        repo = item.get("repo", "")
        if repo and repo not in already_enriched_repos and not item.get("enriched"):
            candidates.append(item)
    
    if not candidates:
        print("  所有候选项目已分析完毕，等待 Scout 发现新项目")
        return
    
    candidates.sort(key=lambda x: x.get("research_score", 0), reverse=True)
    
    print(f"  待分析: {len(candidates)} 个\n")
    
    for i, item in enumerate(candidates[:3]):  # 每次最多分析3个
        candidates[i] = enrich_project(item)
        # 写回 top_candidates 列表
        for j, orig in enumerate(state.get("top_candidates", [])):
            if orig.get("repo") == item.get("repo"):
                state["top_candidates"][j] = item
                break
    
    save_state(state)
    
    # 输出报告
    print(f"\n=== 分析完成 ===")
    print(f"  已分析: {len(candidates[:3])} 个")
    print(f"  候选池总计: {len(state.get('top_candidates', []))}")
    
    # 列出评分最高的3个
    all_buildable = state.get("top_candidates", [])
    all_buildable.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    print(f"\n  当前 TOP 3 候选:")
    for item in all_buildable[:3]:
        name = item.get("repo", "?")
        score = item.get("score", 0)
        has_pricing = item.get("has_pricing", False)
        has_install = item.get("installable", False)
        tag = ""
        if has_pricing: tag += "💰有定价 "
        if has_install: tag += "⚡可装 "
        print(f"    {name} ({score}分) {tag}")

if __name__ == "__main__":
    main()
