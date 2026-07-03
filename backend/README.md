# AlgoForge 後端

FastAPI 後端：代理 LeetCode GraphQL（避開 CORS）、把題目存成 Markdown stub、提供 REST API。

## 安裝

```bash
cd backend
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# Git Bash:            source .venv/Scripts/activate
pip install -r requirements.txt
```

## 用法

### A. CLI 抓題（每天最快）
```bash
python -m app.cli daily          # 每日一題
python -m app.cli 1              # 題號
python -m app.cli two-sum        # titleSlug
python -m app.cli daily --overwrite
```
抓完會在 `data/problems/{id}-{slug}.md` 建立題目 stub（含題目原文 + 8 段空白），
接著用 `@algoforge-coach` 填寫解題分析。

### B. API server（給前端儀表板 S3 用）
```bash
uvicorn app.main:app --reload --port 8642
```

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/health` | 健康檢查 |
| GET | `/api/daily` | 抓每日一題並存 stub |
| GET | `/api/problem/{題號或slug}` | 抓指定題並存 stub |
| GET | `/api/problems` | 列出題目索引 |
| GET | `/api/problems/{id}/note` | 讀某題 Markdown 筆記 |

查詢參數 `?save=false` 只抓不存、`?overwrite=true` 覆寫既有筆記。

## 測試
```bash
pip install pytest
pytest            # htmlmd 轉換測試（不需網路）
```

## 流程定位
後端只建「題目 stub」（frontmatter + 題目原文），8 段解題分析由 `@algoforge-coach` 填。
