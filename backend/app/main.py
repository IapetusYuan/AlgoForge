"""AlgoForge 後端 — FastAPI。

代理 LeetCode GraphQL（避開 CORS），把題目存成 Markdown stub，
並提供 REST API 給前端儀表板（S3）讀取。
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import leetcode, obsidian, solutions, storage

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"

app = FastAPI(title="AlgoForge API", version="0.1.0")

# 前端儀表板（S3）會跨來源呼叫，開發階段全放行
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "algoforge"}


@app.get("/api/daily")
async def daily(save: bool = True, overwrite: bool = False) -> dict:
    """抓 LeetCode 每日一題，預設存成 stub 筆記。"""
    try:
        p = await leetcode.fetch_daily()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"抓每日題失敗：{e}") from e
    result = {k: v for k, v in p.items() if k != "content_html"}
    if save:
        result["saved"] = storage.save_problem(p, overwrite=overwrite)
    return result


@app.get("/api/problem/{identifier}")
async def problem(identifier: str, save: bool = True, overwrite: bool = False) -> dict:
    """抓指定題目（題號或 titleSlug），預設存成 stub 筆記。"""
    try:
        p = await leetcode.fetch_problem(identifier)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"抓題失敗：{e}") from e
    result = {k: v for k, v in p.items() if k != "content_html"}
    if save:
        result["saved"] = storage.save_problem(p, overwrite=overwrite)
    return result


@app.get("/api/problems")
async def problems(sync: bool = True) -> dict:
    """列出題目索引。預設先以筆記 frontmatter 同步（教練的改動會反映進來）。"""
    if sync:
        return {"problems": storage.sync_index_from_notes()}
    return {"problems": storage.list_problems()}


@app.get("/api/stats")
async def stats() -> dict:
    """刷題統計：難度 / 狀態 / 模式分布。"""
    storage.sync_index_from_notes()
    return storage.compute_stats()


@app.get("/api/review")
async def review() -> dict:
    """複習佇列：到期 / 即將複習的題目。"""
    storage.sync_index_from_notes()
    return storage.review_queue()


@app.post("/api/export")
async def export() -> dict:
    """匯出題庫到 Obsidian 知識庫（S5）。"""
    try:
        return obsidian.export_to_vault()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"匯出失敗：{e}") from e


@app.get("/api/problem/{identifier}/solutions")
async def problem_solutions(identifier: str, top: int = 5) -> dict:
    """抓某題社群高票解法（Solutions 區），當儀表板／教練的參考素材。

    非官方 API，僅代理轉發、不落地存原文；抓不到就回空清單，不視為錯誤。
    """
    try:
        slug = identifier if not identifier.isdigit() else await leetcode.resolve_slug_by_id(identifier)
        picks = await solutions.fetch_top_solutions(slug, top=top)
    except (leetcode.LeetCodeError, solutions.SolutionsError):
        picks = []
    return {"identifier": identifier, "solutions": picks}


@app.get("/api/problems/{problem_id}/note")
async def problem_note(problem_id: str) -> dict:
    """讀取某題的 Markdown 筆記內容。"""
    note = storage.get_note(problem_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"找不到題號 {problem_id} 的筆記")
    return {"id": problem_id, "markdown": note}


# 筆記裡的圖示用絕對路徑 /assets/icons/... 引用（GitHub 上也是 repo-root-relative）
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# 前端儀表板（S3）— 掛在最後，API 路由優先匹配
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
