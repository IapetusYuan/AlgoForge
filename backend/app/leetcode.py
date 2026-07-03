"""LeetCode GraphQL client — 抓每日一題與指定題目。

LeetCode 的 GraphQL endpoint 會擋掉沒有合理 Referer / User-Agent 的請求，
所以這裡統一帶上 header，並用 httpx 做非同步請求。
"""
from __future__ import annotations

import httpx

GRAPHQL_URL = "https://leetcode.com/graphql"
# 用來把題號（frontendId）解析成 titleSlug 的官方 REST endpoint
ALL_PROBLEMS_URL = "https://leetcode.com/api/problems/all/"

_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
}

_DAILY_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      questionFrontendId
      title
      titleSlug
      difficulty
      content
      topicTags { name slug }
    }
  }
}
"""

_QUESTION_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    topicTags { name slug }
  }
}
"""


class LeetCodeError(RuntimeError):
    """抓題失敗時拋出。"""


def _normalize(q: dict, *, link: str | None = None, date: str | None = None) -> dict:
    """把 GraphQL 回來的 question 物件整成統一的 dict。"""
    slug = q["titleSlug"]
    return {
        "id": q["questionFrontendId"],
        "title": q["title"],
        "slug": slug,
        "difficulty": q["difficulty"],
        "tags": [t["name"] for t in q.get("topicTags", [])],
        "tag_slugs": [t["slug"] for t in q.get("topicTags", [])],
        "content_html": q.get("content") or "",
        "url": link and f"https://leetcode.com{link}" or f"https://leetcode.com/problems/{slug}/",
        "date": date,
    }


async def _post(client: httpx.AsyncClient, query: str, variables: dict | None = None) -> dict:
    resp = await client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=_HEADERS,
        timeout=20.0,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("errors"):
        raise LeetCodeError(str(payload["errors"]))
    return payload["data"]


async def fetch_daily() -> dict:
    """抓 LeetCode 每日一題。"""
    async with httpx.AsyncClient() as client:
        data = await _post(client, _DAILY_QUERY)
    node = data["activeDailyCodingChallengeQuestion"]
    return _normalize(node["question"], link=node["link"], date=node["date"])


async def fetch_by_slug(slug: str) -> dict:
    """用 titleSlug 抓指定題目，例如 'two-sum'。"""
    async with httpx.AsyncClient() as client:
        data = await _post(client, _QUESTION_QUERY, {"titleSlug": slug})
    q = data.get("question")
    if not q:
        raise LeetCodeError(f"找不到題目：{slug}")
    return _normalize(q)


async def resolve_slug_by_id(frontend_id: int | str) -> str:
    """把題號（如 1）解析成 titleSlug（如 'two-sum'）。"""
    target = str(frontend_id)
    async with httpx.AsyncClient() as client:
        resp = await client.get(ALL_PROBLEMS_URL, headers=_HEADERS, timeout=20.0)
        resp.raise_for_status()
        pairs = resp.json()["stat_status_pairs"]
    for p in pairs:
        if str(p["stat"]["frontend_question_id"]) == target:
            return p["stat"]["question__title_slug"]
    raise LeetCodeError(f"找不到題號：{frontend_id}")


async def fetch_problem(identifier: str) -> dict:
    """通用入口：傳純數字當題號，否則當 titleSlug。"""
    identifier = identifier.strip()
    if identifier.isdigit():
        slug = await resolve_slug_by_id(identifier)
        return await fetch_by_slug(slug)
    return await fetch_by_slug(identifier)
