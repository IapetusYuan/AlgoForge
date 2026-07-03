"""htmlmd 轉換的基本測試（不需網路）。"""
from app.htmlmd import html_to_markdown


def test_paragraph_and_bold():
    raw = "<p>Given an array <strong>nums</strong>.</p>"
    out = html_to_markdown(raw)
    assert "Given an array **nums**." in out


def test_code_and_entities():
    raw = "<p>Return <code>x &lt; y</code></p>"
    out = html_to_markdown(raw)
    assert "`x < y`" in out


def test_pre_block_to_fence():
    raw = "<pre>Input: nums = [2,7]\nOutput: [0,1]</pre>"
    out = html_to_markdown(raw)
    assert out.startswith("```")
    assert "Input: nums = [2,7]" in out
    assert out.rstrip().endswith("```")


def test_list_items():
    raw = "<ul><li>first</li><li>second</li></ul>"
    out = html_to_markdown(raw)
    assert "- first" in out
    assert "- second" in out


def test_empty():
    assert html_to_markdown("") == ""
