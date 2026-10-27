import openai
import argparse
from openai import OpenAI, OpenAIError
import os
import zai


from run_sql2 import DATABASE_PATH, PROJECT_ROOT, execute_query
from report_schema import *
from  pydantic import ValidationError

from report_io import save_report

from usage_log import append_usage_log

import time
from openai.types.chat import ChatCompletion,ChatCompletionChunk

from collections.abc import Iterable
from pathlib import Path




REPORT_PATH = PROJECT_ROOT / "reports" / "model_failure_report.json"

MODEL_NAME = "glm-5.3-flash"
USAGE_LOG_PATH = PROJECT_ROOT / "logs" / "model_usage.jsonl"


def build_summary_prompt(summary: dict[str, int | float]) -> str:
    prompt = (
        f"总记录数为 {summary['total_count']}，"
        f"故障数为 {summary['failure_count']}，"
        f"故障率为 {summary['failure_rate_percent']}%。\n"
        "请根据以上统计数据生成报告，并遵守以下要求：\n"
        "1. 只返回一个合法的 JSON 对象，不要 Markdown 代码围栏或额外说明。\n"
        '2. 仅包含 "total_count"、"failure_count"、"failure_rate_percent"、'
        '"conclusion" 四个字段。\n'
        "3. total_count 和 failure_count 使用整数；failure_rate_percent 使用数字，"
        "不带 %。这三个数值必须与以上统计数据一致，不得自行修改或编造。\n"
        "4. conclusion 使用字符串，用一句话描述这些统计结果，不要推测故障原因。\n"
        "5. 字段名和字符串值使用双引号，不要尾随逗号。"
    )
    return prompt



def request_report(client: OpenAI, prompt: str) -> ChatCompletion:
    for attempt in range(1, 4):
        try:
            response = client.chat.completions.create(
                model="glm-5.3-flash",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=2048,
                extra_body={"thinking": {"type": "enabled"}},
            )
            return response
        except openai.APITimeoutError:
                if attempt == 3:
                    raise

        time.sleep(2 ** (attempt - 1))


def parse_retry_after_seconds(value: str | None) -> int | None:
    if value is None:
        return None
    value=value.strip()
    if value.isascii() and value.isdigit():
        return int(value)


def collect_stream_text(chunks: Iterable[ChatCompletionChunk]) -> str:
    parts=[]
    stop_reason = None
    for chunk in chunks:
        if not chunk.choices:
            continue
        current_reason = chunk.choices[0].finish_reason
        if current_reason is not None:
            stop_reason = current_reason
        text=chunk.choices[0].delta.content
        if text:
            parts.append(text)
            print(text, end="", flush=True)
    if stop_reason == "stop":
        return "".join(parts)
    else:
        raise ValueError(f"结束原因：{stop_reason}")



def request_report_stream(client: OpenAI, prompt: str) -> str:
    # 流式显示并收集正文，结束或出错时关闭流。
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=2048,
        extra_body={"thinking": {"type": "enabled"}},
        stream=True,
    )

    try:
        return collect_stream_text(stream)
    finally:
        stream.close()

def process_report(content: str | None,summary:dict[str, int | float],output_path:Path) -> None:
    if content and content.strip():
        try:
           report=FailureReport.model_validate_json(content)
           if report.total_count!=summary["total_count"] or report.failure_count!=summary["failure_count"] or report.failure_rate_percent!=summary["failure_rate_percent"]:
                print("模型报告与查询结果不一致，请稍后重试。")
                return
        except ValidationError:
            print("报告格式或数据不合法")
            return
        try:
            save_report(report, output_path)
        except OSError:
            print("报告保存失败，请检查输出路径或写入权限。 ")
            return
        print(report.conclusion)
        return
    else:
        print("模型未返回有效正文，请稍后重试。")
        return

def main(use_stream: bool = False):
    sql_path = PROJECT_ROOT / "sql" / "01_failure_summary.sql"
    dataframe = execute_query(DATABASE_PATH, sql_path)
    summary = dataframe.to_dict(orient="records")[0]




    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # api_key = os.getenv("DEEPSEEK_API_KEY")
    #
    # if not api_key:
    #     raise RuntimeError("DEEPSEEK_API_KEY is not configured")

    api_key = os.getenv("ZHIPU_API_KEY")

    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is not configured")
    # client = OpenAI(
    #     api_key=api_key,
    #     base_url="https://open.bigmodel.cn/api/paas/v4",
    # )

    client = OpenAI(
        api_key=api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4",
        timeout=30.0,
        max_retries=0,
    )


    print("Client ready")


    # response = client.chat.completions.create(
    #     model="deepseek-flash",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt,
    #
    #         }
    #     ],
    #     max_tokens=128,
    #     extra_body={"thinking": {"type": "disabled"}},
    # )
    prompt = build_summary_prompt(summary)

    try:
        if use_stream:
            try:
                content = request_report_stream(client, prompt)
                usage=None
                print()

            except ValueError as e:
                print(f"流式回答未完整生成：{e}")
                return
        else:
            response = request_report(client, prompt)
            usage=response.usage
            content=response.choices[0].message.content
    except openai.APITimeoutError:
        print("模型请求超时，请稍后重试。")
        return
    except openai.AuthenticationError:
        print("模型认证失败，请检查 API 密钥。")
        return
    except openai.RateLimitError as error:
        retry_after = error.response.headers.get("retry-after")
        wait_seconds = parse_retry_after_seconds(retry_after)

        if wait_seconds is not None:
            print(f"模型请求受限，服务端建议至少等待 {wait_seconds} 秒后再尝试。")
        else:
            print("模型请求受限，请检查调用频率或账户额度。")

        return
    except openai.APIStatusError as error:
        print(f"模型请求失败，HTTP 状态码：{error.status_code}。")
        return

    try:
        append_usage_log(MODEL_NAME, usage, USAGE_LOG_PATH)
    except OSError:
        print("用量日志保存失败，继续处理模型报告。")
    if usage:
        input_tokens=usage.prompt_tokens
        output_tokens=usage.completion_tokens
        total_tokens=usage.total_tokens
        print(f"token用量信息：\n输入token：{input_tokens}\n输出token：{output_tokens}\n消耗总量：{total_tokens}")
    else:
        if use_stream:
            print("流式 token 用量暂未采集")
        else:
            print("token用量未返回")




    process_report(content,summary,REPORT_PATH)



# print(response.usage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="解析命令行，控制是否流式输出")
    parser.add_argument(
        "--use_stream",
        action="store_true",
        help="使用流式模式生成报告"
    )
    args = parser.parse_args()
    main(args.use_stream)
