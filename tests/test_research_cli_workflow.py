from research_platform.cli_workflow import guide_text


def test_guide_mentions_cli_commands():
    text = guide_text()
    assert "research db up" in text
    assert "research quickstart" in text
    assert "walk-forward" in text
