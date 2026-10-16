from pathlib import Path
import json


def summarize_usage_log(input_path: Path, model: str) -> dict[str, int]:
    d={
    "request_count": 0,
    "missing_usage_count": 0,
    "known_prompt_tokens": 0,
    "known_completion_tokens": 0,
    "known_total_tokens": 0,
}
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            record = json.loads(line)
            if record["model"]!=model:
                continue
            else:
                d["request_count"]+=1
                if record["prompt_tokens"] is None or record["completion_tokens"] is None or record["total_tokens"] is None:
                    d["missing_usage_count"]+=1
                else:
                    d["known_prompt_tokens"]+=record["prompt_tokens"]
                    d["known_completion_tokens"]+=record["completion_tokens"]
                    d["known_total_tokens"]+=record["total_tokens"]

    return d
