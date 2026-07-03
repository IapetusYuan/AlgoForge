"""obsidian 匯出測試（寫到臨時 vault，不碰真實 vault）。"""
from app import obsidian, storage


def test_link_patterns_injects_wikilinks():
    md = "---\nid: 1\n---\n\n# 1. Two Sum\n\n內文"
    out = obsidian._link_patterns(md, ["hash-map", "complement-lookup"])
    assert "**模式**：[[模式/hash-map]], [[模式/complement-lookup]]" in out


def test_export_builds_bank_pattern_index(tmp_path, monkeypatch):
    sample = [
        {"id": "1", "title": "Two Sum", "slug": "two-sum", "difficulty": "Easy",
         "tags": [], "patterns": ["hash-map"], "date_solved": "", "revisit": None,
         "status": "solved", "url": ""},
    ]
    monkeypatch.setattr(storage, "sync_index_from_notes", lambda: sample)
    monkeypatch.setattr(storage, "get_note", lambda pid: "---\nid: 1\n---\n\n# 1. Two Sum\n")

    result = obsidian.export_to_vault(vault=tmp_path)

    assert result["problems"] == 1
    assert result["patterns"] == 1
    assert (tmp_path / "題庫" / "1-two-sum.md").exists()
    assert (tmp_path / "模式" / "hash-map.md").exists()
    assert (tmp_path / "題庫索引.md").exists()
    # 模式頁要反向連到題目
    pat = (tmp_path / "模式" / "hash-map.md").read_text(encoding="utf-8")
    assert "[[題庫/1-two-sum]]" in pat
