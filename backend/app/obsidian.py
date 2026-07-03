"""S5 知識庫整合 — 把解過的題與模式匯出成 Obsidian 互連 wiki。

產出（預設寫到 D:\\Iapetus\\AlgoForge\\題庫\\，可用環境變數 ALGOFORGE_VAULT 覆蓋）：
- 題庫/{id}-{slug}.md   ：題目筆記（patterns 改寫成 [[模式/x]] 雙向連結）
- 模式/{pattern}.md      ：每個解題模式一頁，列出採用該模式的所有題目（反向連結）
- 題庫索引.md            ：總覽 + 依難度/模式分類

設計：repo 的 data/problems/ 仍是真實來源；這裡產出「複習用」的知識圖譜。
"""
from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

from . import storage


def _vault_root() -> Path:
    return Path(os.environ.get("ALGOFORGE_VAULT", r"D:\Iapetus\AlgoForge"))


def _link_patterns(md: str, patterns: list[str]) -> str:
    """把筆記 frontmatter 的 patterns 行改寫成 [[模式/x]] 連結，方便 Obsidian 跳轉。"""
    if not patterns:
        return md
    links = ", ".join(f"[[模式/{p}]]" for p in patterns)
    # 在標題下方插入一行「模式：」連結（frontmatter 後第一個 H1 之後）
    return re.sub(
        r"(^# .+?$)",
        rf"\1\n\n**模式**：{links}",
        md,
        count=1,
        flags=re.M,
    )


def export_to_vault(vault: Path | None = None) -> dict:
    """匯出整個題庫到 Obsidian。回傳寫了哪些檔。"""
    vault = vault or _vault_root()
    problems = storage.sync_index_from_notes()

    bank_dir = vault / "題庫"
    pat_dir = vault / "模式"
    bank_dir.mkdir(parents=True, exist_ok=True)
    pat_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    by_pattern: dict[str, list[dict]] = defaultdict(list)

    # 1) 題目頁
    for p in problems:
        note = storage.get_note(p["id"]) or ""
        note = _link_patterns(note, p.get("patterns", []))
        fname = f"{p['id']}-{p['slug']}.md"
        (bank_dir / fname).write_text(note, encoding="utf-8")
        written.append(f"題庫/{fname}")
        for pat in p.get("patterns", []):
            by_pattern[pat].append(p)

    # 2) 模式頁（反向連結）
    for pat, probs in sorted(by_pattern.items()):
        lines = [
            "---",
            "tags: [解題模式, AlgoForge]",
            f"summary: 採用「{pat}」模式的題目彙整",
            "---",
            "",
            f"# 模式：{pat}",
            "",
            f"> 採用此模式的題目共 {len(probs)} 題。看到對應特徵就該想到這招。",
            "",
            "## 題目",
        ]
        for p in sorted(probs, key=lambda x: int(x["id"]) if str(x["id"]).isdigit() else 0):
            lines.append(f"- [[題庫/{p['id']}-{p['slug']}]] — {p['title']}（{p['difficulty']}）")
        lines += ["", "## 相關", "- [[題庫索引]]", "- [[解題模式庫]]（總覽對照表）", ""]
        (pat_dir / f"{pat}.md").write_text("\n".join(lines), encoding="utf-8")
        written.append(f"模式/{pat}.md")

    # 3) 題庫索引
    idx_lines = [
        "---",
        "tags: [索引, AlgoForge, 題庫]",
        "summary: AlgoForge 已解題目與解題模式的知識圖譜入口",
        "---",
        "",
        "# 題庫索引",
        "",
        f"> 已收錄 {len(problems)} 題、{len(by_pattern)} 種解題模式。",
        "",
        "## 依模式",
    ]
    for pat, probs in sorted(by_pattern.items(), key=lambda kv: -len(kv[1])):
        idx_lines.append(f"- [[模式/{pat}]]（{len(probs)}）")
    idx_lines += ["", "## 依難度"]
    by_diff: dict[str, list[dict]] = defaultdict(list)
    for p in problems:
        by_diff[p.get("difficulty", "?")].append(p)
    for diff in ["Easy", "Medium", "Hard"]:
        if diff in by_diff:
            idx_lines.append(f"### {diff}")
            for p in by_diff[diff]:
                idx_lines.append(f"- [[題庫/{p['id']}-{p['slug']}]] — {p['title']}")
    idx_lines += ["", "## 相關", "- [[_INDEX]]（專案總覽）", "- [[解題模式庫]]", ""]
    (vault / "題庫索引.md").write_text("\n".join(idx_lines), encoding="utf-8")
    written.append("題庫索引.md")

    return {
        "vault": str(vault),
        "problems": len(problems),
        "patterns": len(by_pattern),
        "files_written": written,
    }
