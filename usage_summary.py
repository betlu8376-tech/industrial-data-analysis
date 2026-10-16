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




def estimate_token_cost(prompt_tokens: int,completion_tokens: int,input_price_per_million: float,output_price_per_million: float,)->float:
    if prompt_tokens <0 or completion_tokens <0 or input_price_per_million<0 or output_price_per_million<0:
        raise ValueError("不能出现负数")
    input_cost = prompt_tokens/1000000 * input_price_per_million
    output_cost = completion_tokens/1000000 * output_price_per_million
    return input_cost + output_cost

