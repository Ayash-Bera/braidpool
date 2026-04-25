from eval.metrics import wer, cer, MetricsResult

def test_perfect_match():
    result = wer("hello world", "hello world")
    assert result == 0.0

def test_one_word_wrong():
    result = wer("hello world", "hello bitcoin")
    assert 0.0 < result <= 0.5

def test_cer_char_level():
    result = cer("abc", "axc")
    assert 0.0 < result <= 0.5

def test_returns_none_when_reference_is_none():
    result = wer(None, "anything")
    assert result is None

def test_metrics_result_dataclass():
    m = MetricsResult(wer=0.1, cer=0.05)
    assert m.wer == 0.1
    assert m.cer == 0.05
