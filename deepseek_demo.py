import openai
from fontTools.unicodedata import script
from openai import OpenAI
import os
import zai
from run_sql2 import DATABASE_PATH, PROJECT_ROOT, execute_query





def build_summary_prompt(summary: dict[str, int | float]) -> str:
    prompt = (
        f"总记录数为 {summary['total_count']}，"
        f"故障数为 {summary['failure_count']}，"
        f"故障率为 {summary['failure_rate_percent']}%。"
        "请用一句话说明这些统计结果，不要推测故障原因。"
    )
    return prompt

def main():
    sql_path = PROJECT_ROOT / "sql" / "01_failure_summary.sql"
    dataframe = execute_query(DATABASE_PATH, sql_path)
    summary = dataframe.to_dict(orient="records")[0]

    print(summary)

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

    prompt=build_summary_prompt(summary)
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
    except openai.APITimeoutError:
        print("模型请求超时，请稍后重试。")
        return

    content=response.choices[0].message.content
    if content and content.strip():
        print(content)
        return
    else:
        print("模型未返回有效正文，请稍后重试。")
        return



# print(response.usage)

if __name__ == "__main__":
    main()