from hope.apps.steficon.templatetags.engine import HtmlDiff


def test_html_diff_make_table_produces_html():
    diff = HtmlDiff()
    result = diff.make_table(["line1\n", "line2\n"], ["line1\n", "changed\n"], "before", "after")
    assert "<table" in result
    assert "before" in result
    assert "after" in result
