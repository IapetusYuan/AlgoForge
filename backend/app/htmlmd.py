"""把 LeetCode 題目的 HTML 內容轉成精簡 Markdown / 純文字。

LeetCode 題幹是 HTML（含 <pre>、<code>、<sup>、實體符號等）。
不引入額外重依賴，用標準庫做夠用的轉換：保留段落、程式碼區塊、清單。
"""
from __future__ import annotations

import html
import re

_BLOCK_PRE = re.compile(r"<pre>(.*?)</pre>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")


def html_to_markdown(raw: str) -> str:
    if not raw:
        return ""
    text = raw

    # <pre>…</pre> → fenced code block（先抽出避免被後面規則破壞）
    blocks: list[str] = []

    def _stash(m: re.Match) -> str:
        inner = _TAG.sub("", m.group(1))
        inner = html.unescape(inner).strip("\n")
        blocks.append(inner)
        return f"\x00BLOCK{len(blocks) - 1}\x00"

    text = _BLOCK_PRE.sub(_stash, text)

    # 結構性標籤 → Markdown
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<li>", "- ", text, flags=re.I)
    text = re.sub(r"</li>", "\n", text, flags=re.I)
    text = re.sub(r"<(strong|b)>", "**", text, flags=re.I)
    text = re.sub(r"</(strong|b)>", "**", text, flags=re.I)
    text = re.sub(r"<(em|i)>", "*", text, flags=re.I)
    text = re.sub(r"</(em|i)>", "*", text, flags=re.I)
    text = re.sub(r"<code>", "`", text, flags=re.I)
    text = re.sub(r"</code>", "`", text, flags=re.I)
    text = re.sub(r"<sup>", "^", text, flags=re.I)

    # 其餘標籤一律去除
    text = _TAG.sub("", text)
    text = html.unescape(text)

    # 還原程式碼區塊
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00BLOCK{i}\x00", f"```\n{block}\n```")

    # 收斂多餘空行
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
