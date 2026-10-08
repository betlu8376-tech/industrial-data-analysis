from deepseek_demo import build_summary_prompt


def test_build_summary_prompt() -> None:
    summary = {
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }

    prompt = build_summary_prompt(summary)

    assert "总记录数为 10000" in prompt
    assert "故障数为 339" in prompt
    assert "故障率为 3.39%" in prompt
    assert "不要推测故障原因" in prompt


def test_build_summary_prompt_with_different_data() -> None:
    summary = {
        "total_count": 200,
        "failure_count": 10,
        "failure_rate_percent": 5.0,
    }

    prompt = build_summary_prompt(summary)

    assert "总记录数为 200" in prompt
    assert "故障数为 10" in prompt
    assert "故障率为 5.0%" in prompt
    assert "不要推测故障原因" in prompt