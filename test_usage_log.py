from pathlib import Path


import json
from pathlib import Path
from openai.types.completion_usage import CompletionUsage
from usage_log import append_usage_log



def test_append_usage_log_preserves_records(tmp_path:Path):
    output_path =tmp_path / "nested" / "usage.jsonl"
    append_usage_log("glm-5.3-flash",CompletionUsage(prompt_tokens=120,completion_tokens=80,total_tokens=200),output_path)
    append_usage_log("glm-5.3-flash",CompletionUsage(prompt_tokens=0,completion_tokens=0,total_tokens=0),output_path)
    with output_path.open("r",encoding="utf-8") as file:

        lines = file.read().splitlines()
        logs = [json.loads(line) for line in lines]


        assert len(logs) == 2
        assert logs[0]["model"]== "glm-5.3-flash"
        assert logs[1]["model"]== "glm-5.3-flash"
        assert logs[0]["prompt_tokens"] == 120
        assert logs[0]["completion_tokens"] == 80
        assert logs[0]["total_tokens"] == 200
        assert logs[1]["prompt_tokens"] == 0
        assert logs[1]["completion_tokens"] == 0
        assert logs[1]["total_tokens"] == 0


def test_append_usage_log_handles_missing_usage(tmp_path:Path):
    output_path =tmp_path / "nested" / "usage.jsonl"
    append_usage_log("glm-5.3-flash",None,output_path)
    with output_path.open("r",encoding="utf-8") as file:


        lines = file.read().splitlines()
        logs = [json.loads(line) for line in lines]


        assert len(logs) == 1
        assert logs[0]["model"]== "glm-5.3-flash"
        assert logs[0]["prompt_tokens"] is None
        assert logs[0]["completion_tokens"] is None
        assert logs[0]["total_tokens"] is None
