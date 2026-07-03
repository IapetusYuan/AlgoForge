"""資料層 — 把抓到的題目存成 Markdown 筆記（套模板）並維護 index.json。

設計：後端只建立「題目 stub」——填好 frontmatter + 題目原文，
8 段解題分析留空，交給 AlgoForge 解題教練 agent 之後填。
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .htmlmd import html_to_markdown

# 專案根目錄：backend/app/storage.py → 上溯三層
ROOT = Path(__file__).resolve().parents[2]
PROBLEMS_DIR = ROOT / "data" / "problems"
INDEX_PATH = ROOT / "data" / "index.json"
TEMPLATE_PATH = ROOT / "templates" / "problem-note.md"


def _slugify_filename(problem_id: str, slug: str) -> str:
    return f"{problem_id}-{slug}.md"


def note_path(problem_id: str, slug: str) -> Path:
    return PROBLEMS_DIR / _slugify_filename(problem_id, slug)


def _render_note(p: dict) -> str:
    """用 problem-note 模板的結構，產出題目 stub。"""
    statement = html_to_markdown(p["content_html"])
    today = date.today().isoformat()
    tags = ", ".join(p["tags"])
    return f"""---
id: {p['id']}
title: {p['title']}
slug: {p['slug']}
difficulty: {p['difficulty']}
tags: [{tags}]
url: {p['url']}
patterns: []
time_complexity:
space_complexity:
date_solved: {today}
revisit:
status: stuck
---

# {p['id']}. {p['title']}

> {p['difficulty']} · {tags} · [原題連結]({p['url']})

## 題目原文
{statement}

---
<!-- 以下 8 段由 @algoforge-coach 填寫 -->

## 1. 題目摘要

## 2. 怎麼切入這題（思維框架）

## 3. 核心觀念

## 4. 解法
### Java（主）
```java
```
### C++（次）
```cpp
```

## 5. 時間複雜度推導

## 6. 空間複雜度推導

## 7. 模式歸納

## 8. 踩坑 / 易錯點
"""


def save_problem(p: dict, *, overwrite: bool = False) -> dict:
    """把題目寫成 stub 筆記並更新 index。回傳 index 條目。"""
    PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
    path = note_path(p["id"], p["slug"])
    created = not path.exists()
    if created or overwrite:
        path.write_text(_render_note(p), encoding="utf-8")
    entry = _update_index(p)
    entry["created"] = created
    entry["path"] = str(path.relative_to(ROOT)).replace("\\", "/")
    return entry


def _load_index() -> dict:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {"meta": {"project": "AlgoForge", "schema_version": 1}, "problems": []}


def _update_index(p: dict) -> dict:
    idx = _load_index()
    idx["meta"]["updated_at"] = date.today().isoformat()
    entry = {
        "id": p["id"],
        "title": p["title"],
        "slug": p["slug"],
        "difficulty": p["difficulty"],
        "tags": p["tags"],
        "patterns": [],
        "date_solved": date.today().isoformat(),
        "revisit": None,
        "status": "stuck",
        "url": p["url"],
    }
    problems = [q for q in idx["problems"] if q["id"] != p["id"]]
    problems.append(entry)
    problems.sort(key=lambda q: int(q["id"]) if str(q["id"]).isdigit() else 0)
    idx["problems"] = problems
    INDEX_PATH.write_text(
        json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return entry


def list_problems() -> list[dict]:
    return _load_index()["problems"]


def get_note(problem_id: str) -> str | None:
    matches = list(PROBLEMS_DIR.glob(f"{problem_id}-*.md"))
    if not matches:
        return None
    return matches[0].read_text(encoding="utf-8")


# ===== S4：以筆記 frontmatter 為真實來源同步 index、統計、複習佇列 =====

def _parse_frontmatter(text: str) -> dict:
    """極簡 frontmatter 解析（只取 key: value，夠用即可，不引 yaml）。"""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm


def _parse_list(val: str) -> list[str]:
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
    return [val] if val else []


def sync_index_from_notes() -> list[dict]:
    """重掃 data/problems/ 的筆記 frontmatter，重建 index。

    筆記是真實來源：解題教練改了 status/patterns/revisit，這裡會同步進 index。
    """
    idx = _load_index()
    problems: list[dict] = []
    for path in sorted(PROBLEMS_DIR.glob("*.md")):
        fm = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fm.get("id"):
            continue
        revisit = fm.get("revisit", "").strip() or None
        problems.append({
            "id": str(fm.get("id")),
            "title": fm.get("title", ""),
            "slug": fm.get("slug", ""),
            "difficulty": fm.get("difficulty", ""),
            "tags": _parse_list(fm.get("tags", "")),
            "patterns": _parse_list(fm.get("patterns", "")),
            "date_solved": fm.get("date_solved", ""),
            "revisit": revisit,
            "status": fm.get("status", "stuck"),
            "url": fm.get("url", ""),
        })
    problems.sort(key=lambda q: int(q["id"]) if str(q["id"]).isdigit() else 0)
    idx["problems"] = problems
    idx["meta"]["updated_at"] = date.today().isoformat()
    INDEX_PATH.write_text(
        json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return problems


def compute_stats() -> dict:
    """刷題統計：依難度 / 狀態 / 模式分布。"""
    from collections import Counter

    problems = list_problems()
    diff: Counter = Counter()
    status: Counter = Counter()
    pattern: Counter = Counter()
    for p in problems:
        diff[p.get("difficulty", "?")] += 1
        status[p.get("status", "?")] += 1
        for x in p.get("patterns", []):
            pattern[x] += 1
    return {
        "total": len(problems),
        "by_difficulty": dict(diff),
        "by_status": dict(status),
        "by_pattern": dict(pattern.most_common()),
    }


def review_queue(today: str | None = None) -> dict:
    """複習佇列：revisit 日期 <= 今天 = 到期；之後 = 即將。"""
    today = today or date.today().isoformat()
    due: list[dict] = []
    upcoming: list[dict] = []
    for p in list_problems():
        revisit = p.get("revisit")
        if not revisit:
            continue
        item = {
            "id": p["id"],
            "title": p["title"],
            "difficulty": p["difficulty"],
            "revisit": revisit,
            "patterns": p.get("patterns", []),
        }
        (due if revisit <= today else upcoming).append(item)
    due.sort(key=lambda x: x["revisit"])
    upcoming.sort(key=lambda x: x["revisit"])
    return {"today": today, "due": due, "upcoming": upcoming}
