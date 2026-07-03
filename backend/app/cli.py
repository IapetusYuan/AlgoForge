"""命令列抓題 — 不開 server 也能用。

用法：
    python -m app.cli daily            # 抓每日一題
    python -m app.cli 1                # 抓題號 1
    python -m app.cli two-sum          # 抓 titleSlug
    python -m app.cli daily --overwrite
    python -m app.cli export           # 匯出題庫到 Obsidian 知識庫（S5）
"""
from __future__ import annotations

import argparse
import asyncio

from . import leetcode, obsidian, storage


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


def main() -> None:
    parser = argparse.ArgumentParser(description="AlgoForge 抓題 / 匯出 CLI")
    parser.add_argument("target", help="daily / 題號 / titleSlug / export")
    parser.add_argument("--overwrite", action="store_true", help="覆寫既有筆記")
    args = parser.parse_args()
    if args.target == "export":
        _export()
    else:
        asyncio.run(_fetch(args.target, args.overwrite))


if __name__ == "__main__":
    main()
