"""命令列抓題 — 不開 server 也能用。

用法：
    python -m app.cli daily            # 抓每日一題
    python -m app.cli 1                # 抓題號 1
    python -m app.cli two-sum          # 抓 titleSlug
    python -m app.cli daily --overwrite
    python -m app.cli export           # 匯出題庫到 Obsidian 知識庫（S5）
    python -m app.cli solutions 1      # 抓題號 1 的社群高票解法（給教練當參考素材）
    python -m app.cli solutions two-sum --top 3
"""
from __future__ import annotations

import argparse
import asyncio

from . import leetcode, obsidian, solutions, storage


async def _fetch(target: str, overwrite: bool) -> None:
    if target == "daily":
        p = await leetcode.fetch_daily()
    else:
        p = await leetcode.fetch_problem(target)
    entry = storage.save_problem(p, overwrite=overwrite)
    action = "建立" if entry["created"] else ("覆寫" if overwrite else "已存在（未動）")
    print(f"[{action}] {p['id']}. {p['title']} ({p['difficulty']})")
    print(f"  tags: {', '.join(p['tags'])}")
    print(f"  note: {entry['path']}")
    print("  下一步：用 @algoforge-coach 填寫 8 段解題分析")


def _export() -> None:
    result = obsidian.export_to_vault()
    print(f"[匯出] {result['problems']} 題、{result['patterns']} 種模式 → {result['vault']}")
    for f in result["files_written"]:
        print(f"  + {f}")


async def _solutions(target: str, top: int) -> None:
    """印出社群高票解法（Markdown），給教練分析時讀取當參考素材。

    失敗就印一句提示後直接結束（exit code 0）——這是選讀的參考素材，
    不該讓教練的分析流程因為抓不到而卡住。
    """
    slug = target if not target.isdigit() else await leetcode.resolve_slug_by_id(target)
    try:
        picks = await solutions.fetch_top_solutions(slug, top=top)
    except solutions.SolutionsError as e:
        print(f"[社群解法] 抓取失敗，略過此段即可：{e}")
        return
    if not picks:
        print("[社群解法] 該題目前沒有討論區文章可參考。")
        return
    for p in picks:
        print(f"\n## {p['title']}（by {p['author']}，{p['upvotes']} 讚）")
        print(f"原文：{p['url']}\n")
        print(p["content_md"])
        print("\n---")


def main() -> None:
    parser = argparse.ArgumentParser(description="AlgoForge 抓題 / 匯出 CLI")
    parser.add_argument("target", help="daily / 題號 / titleSlug / export / solutions")
    parser.add_argument("problem", nargs="?", help="solutions 用：題號或 titleSlug")
    parser.add_argument("--overwrite", action="store_true", help="覆寫既有筆記")
    parser.add_argument("--top", type=int, default=5, help="solutions：取前幾篇高票解法（預設 5）")
    args = parser.parse_args()
    if args.target == "export":
        _export()
    elif args.target == "solutions":
        if not args.problem:
            parser.error("用法：python -m app.cli solutions <題號|slug> [--top N]")
        asyncio.run(_solutions(args.problem, args.top))
    else:
        asyncio.run(_fetch(args.target, args.overwrite))


if __name__ == "__main__":
    main()
