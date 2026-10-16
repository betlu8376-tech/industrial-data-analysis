
from usage_log import append_usage_log
from pathlib import Path
from openai.types.completion_usage import CompletionUsage
from usage_summary import summarize_usage_log,estimate_token_cost

import pytest

def test_usage_summary(tmp_path:Path):
    output_path =tmp_path / "nested" / "usage.jsonl"
    append_usage_log("glm-5.3-flash", CompletionUsage(prompt_tokens=120, completion_tokens=80, total_tokens=200),
                     output_path)
    append_usage_log("glm-5.3-flash", CompletionUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                     output_path)
    append_usage_log("glm-5.3-flash", None,
                     output_path)
    append_usage_log("deepseek-flash", CompletionUsage(prompt_tokens=250, completion_tokens=100, total_tokens=350),
                     output_path)
    summary_usage_data=summarize_usage_log(output_path,"glm-5.3-flash")
    assert summary_usage_data=={
        "request_count": 3,
        "missing_usage_count": 1,
        "known_prompt_tokens": 120,
        "known_completion_tokens": 80,
        "known_total_tokens": 200,
}



def test_empty_usage_summary(tmp_path:Path):
    input_path = tmp_path / "nested" / "usage.jsonl"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.touch()
    data=summarize_usage_log(input_path,"glm-5.3-flash")
    assert data=={
        "request_count": 0,
        "missing_usage_count": 0,
        "known_prompt_tokens": 0,
        "known_completion_tokens": 0,
        "known_total_tokens": 0,
}


@pytest.mark.parametrize(
    "usage_conditions",
    [[1000,500,2.0,8.0,0.006],[0,0,2.0,8.0,0]],
    ids=["normal","zero"]

)
def test_usage_cost(usage_conditions:list[int | float]):
    total_cost=estimate_token_cost(usage_conditions[0],usage_conditions[1],usage_conditions[2],usage_conditions[3])
    assert total_cost==pytest.approx(usage_conditions[4])

    with pytest.raises(ValueError):
        estimate_token_cost(0,0,-2.0,8.0)



