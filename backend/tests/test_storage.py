"""storage 的 S4 邏輯測試（frontmatter 解析 / 複習佇列），不需網路。"""
from app import storage


def test_parse_frontmatter():
    text = "---\nid: 1\ntitle: Two Sum\npatterns: [hash-map, complement-lookup]\nrevisit: 2026-06-29\n---\n\n# body"
    fm = storage._parse_frontmatter(text)
    assert fm["id"] == "1"
    assert fm["title"] == "Two Sum"
    assert fm["revisit"] == "2026-06-29"


def test_parse_list():
    assert storage._parse_list("[a, b, c]") == ["a", "b", "c"]
    assert storage._parse_list("[]") == []
    assert storage._parse_list("") == []


def test_parse_frontmatter_no_fm():
    assert storage._parse_frontmatter("# just a heading") == {}


def test_review_queue_split(monkeypatch):
    sample = [
        {"id": "1", "title": "A", "difficulty": "Easy", "revisit": "2026-01-01", "patterns": []},
        {"id": "2", "title": "B", "difficulty": "Hard", "revisit": "2099-01-01", "patterns": []},
        {"id": "3", "title": "C", "difficulty": "Easy", "revisit": None, "patterns": []},
    ]
    monkeypatch.setattr(storage, "list_problems", lambda: sample)
    q = storage.review_queue(today="2026-06-23")
    assert [x["id"] for x in q["due"]] == ["1"]        # 過期 → 到期
    assert [x["id"] for x in q["upcoming"]] == ["2"]   # 未來 → 即將
    # id 3 沒有 revisit → 不進佇列


def test_compute_stats(monkeypatch):
    sample = [
        {"difficulty": "Easy", "status": "solved", "patterns": ["hash-map"]},
        {"difficulty": "Medium", "status": "solved", "patterns": ["greedy", "hash-map"]},
    ]
    monkeypatch.setattr(storage, "list_problems", lambda: sample)
    s = storage.compute_stats()
    assert s["total"] == 2
    assert s["by_difficulty"] == {"Easy": 1, "Medium": 1}
    assert s["by_pattern"]["hash-map"] == 2
