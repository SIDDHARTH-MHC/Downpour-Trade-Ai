from engine.news_aggregator import FEED_SOURCES, _dedupe_key, _normalize_title, tag_sentiment, tag_symbols


def test_feed_sources_include_block_bybit_okx():
    ids = {s.feed_id for s in FEED_SOURCES}
    assert {"theblock", "bybit_ann", "okx_ann"}.issubset(ids)


def test_tag_symbols_btc():
    assert "BTC" in tag_symbols("Bitcoin hits new milestone")


def test_tag_sentiment_bearish():
    assert tag_sentiment("Exchange hack leads to liquidation cascade") == "Bearish"


def test_dedupe_same_title():
    k1 = _dedupe_key("Bitcoin Rises", "https://a.com/1")
    k2 = _dedupe_key("Bitcoin Rises", "https://a.com/1")
    assert k1 == k2
    assert _normalize_title("Hello, World!") == "hello world"
