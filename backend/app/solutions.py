"""LeetCode 社群解法 client — 抓討論區（Solutions 區）高票文章當教練參考素材。

跟 leetcode.py 用同一組 GraphQL endpoint（ugcArticle 體系），一樣免登入。
內容本來就是 Markdown，不用經過 htmlmd 轉換。

只回傳供 coach agent 判讀的候選素材，不落地存原文 —— 筆記裡最終只留
「連結 + agent 自己改寫的講解」，尊重原作者著作權。
"""
from __future__ import annotations

import httpx

from .leetcode import _HEADERS, GRAPHQL_URL

_LIST_QUERY = """
query ugcArticleSolutionArticles(
  $questionSlug: String!
  $orderBy: ArticleOrderByEnum
  $tagSlugs: [String!]
  $skip: Int
  $first: Int
) {
  ugcArticleSolutionArticles(
    questionSlug: $questionSlug
    orderBy: $orderBy
    tagSlugs: $tagSlugs
    skip: $skip
    first: $first
  ) {
    edges {
      node {
        title
        summary
        topicId
        author { userName }
        reactions { count reactionType }
      }
    }
  }
}
"""

_ARTICLE_QUERY = """
query ugcArticleSolutionArticle($topicId: ID) {
  ugcArticleSolutionArticle(topicId: $topicId) {
    title
    content
    author { userName }
  }
}
"""


class SolutionsError(RuntimeError):
    """抓社群解法失敗時拋出 —— 呼叫端應捕捉並優雅降級（略過此段，不影響主流程）。"""


def _upvotes(reactions: list[dict]) -> int:
    for r in reactions:
        if r.get("reactionType") == "UPVOTE":
            return r.get("count", 0)
    return 0


async def fetch_top_solutions(slug: str, *, top: int = 5) -> list[dict]:
    """抓某題 Solutions 區按讚數排序的 top N 篇全文，當作教練精選的候選池。"""
    try:
        async with httpx.AsyncClient() as client:
            list_resp = await client.post(
                GRAPHQL_URL,
                json={
                    "query": _LIST_QUERY,
                    "variables": {
                        "questionSlug": slug,
                        "orderBy": "MOST_VOTES",
                        "tagSlugs": [],
                        "skip": 0,
                        "first": top,
                    },
                },
                headers=_HEADERS,
                timeout=20.0,
            )
            list_resp.raise_for_status()
            list_payload = list_resp.json()
            if list_payload.get("errors"):
                raise SolutionsError(str(list_payload["errors"]))
            edges = list_payload["data"]["ugcArticleSolutionArticles"]["edges"]

            results: list[dict] = []
            for edge in edges:
                node = edge["node"]
                topic_id = node["topicId"]
                article_resp = await client.post(
                    GRAPHQL_URL,
                    json={"query": _ARTICLE_QUERY, "variables": {"topicId": topic_id}},
                    headers=_HEADERS,
                    timeout=20.0,
                )
                article_resp.raise_for_status()
                article_payload = article_resp.json()
                article = (article_payload.get("data") or {}).get("ugcArticleSolutionArticle")
                if not article:
                    continue
                results.append(
                    {
                        "title": node["title"],
                        "author": node["author"]["userName"],
                        "upvotes": _upvotes(node.get("reactions", [])),
                        "url": f"https://leetcode.com/problems/{slug}/solutions/{topic_id}/",
                        "content_md": article["content"],
                    }
                )
            return results
    except (httpx.HTTPError, KeyError, TypeError) as e:
        raise SolutionsError(f"抓社群解法失敗（{slug}）：{e}") from e
