import os
import argparse
from api import load_product_type_summary
from openai import OpenAI
import json

MODEL_NAME = "deepseek-flash"
tools=[
    {
        "type":"function",
        "function":{
            "name":"load_product_type_summary",
            "description":"查询各产品类型的总记录数、故障数和故障率，用于比较不同产品类型的故障情况。",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
            }
        }
    }
]


def execute_tool(tool_name: str) -> list[dict[str, str | int | float]]:
    if tool_name == "load_product_type_summary" :
        return load_product_type_summary()
    raise ValueError(f"未知工具：{tool_name}")


def request_tool_call(client: OpenAI, question: str):
    response=client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": question}
        ],
        max_tokens=2048,
        extra_body={"thinking": {"type": "disabled"}},
        tools=tools,
        tool_choice="auto"
    )
    return response.choices[0].message


def answer_question(client: OpenAI, question: str) -> str:
    message=request_tool_call(client, question)
    if not message.tool_calls:
        return message.content or ""
    messages = [{"role": "user", "content": question}]
    messages.append(message.model_dump(exclude_none=True))
    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        if arguments != {}:
            raise ValueError("该调用不应有参数")
        result = execute_tool(tool_name)
        print(f"已执行工具：{tool_name}，返回 {len(result)} 条记录")
        result_text = json.dumps(result, ensure_ascii=False)
        messages.append({"role": "tool",
                         "tool_call_id": tool_call.id,
                         "content": result_text})
    final_response=client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=2048,
        extra_body={"thinking": {"type": "disabled"}},
    )
    return final_response.choices[0].message.content or ""



def main(question: str):
    question=question.strip()
    if not question:
        print("问题不能为空")
        return
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("API_KEY ERROR")
        return
    # client = OpenAI(
    #     api_key=api_key,
    #     base_url="https://open.bigmodel.cn/api/paas/v4",
    #     timeout=30.0,
    #     max_retries=0,
    # )

    with OpenAI(api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=30.0,
        max_retries=0,) as client:
        answer = answer_question(client, question)
        print(answer)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="询问问题")
    parser.add_argument(
        "question",
        type=str,
        help="要询问的设备故障分析问题"

    )
    args = parser.parse_args()
    main(args.question)
