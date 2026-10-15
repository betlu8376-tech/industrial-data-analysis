import json
from pathlib import Path

from openai.types.completion_usage import CompletionUsage


def append_usage_log(
    model: str,
    usage: CompletionUsage | None,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if usage is None:
        d = {
            "model": model,
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }
    else:
        d={"model":model,
           "prompt_tokens":usage.prompt_tokens,
           "completion_tokens":usage.completion_tokens,
           "total_tokens":usage.total_tokens
           }
    with output_path.open("a", encoding="utf-8") as usage_log:
        need_json=json.dumps(d)
        usage_log.write(need_json + "\n")

