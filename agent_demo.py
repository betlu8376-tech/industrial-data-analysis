import os
import argparse
from api import load_product_type_summary,load_product_torque_summary,load_product_wear_summary
from openai import OpenAI
import json

import sqlite3
import pandas as pd

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
    },

    {
        "type":"function",
        "function":{
            "name":"load_product_wear_summary",
            "description":"各刀具磨损时间区间的故障统计",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
            }
        }
    },

{
        "type":"function",
        "function":{
            "name":"load_product_torque_summary",
            "description":"各扭矩区间的故障统计",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
            }
        }
    },

    {
        "type":"function",
        "function":{
            "name":"get_product_type_summary",
            "description":"查询指定产品类型的总记录数、故障数和故障率，适用于只查询 L、M 或 H 类型的请求",
            "parameters":{
                "type":"object",
                "properties":{
                    "product_type":{"type":"string","description":"要查询的产品类型","enum":["L","H","M"]}
                },
                "required":["product_type"]
            }

        }
    }
]


def execute_tool(tool_name: str,arguments: dict[str, object]) -> list[dict[str, str | int | float]]:
    if not isinstance(arguments, dict):
        raise ValueError("arguments 必须是字典")
    if tool_name == "load_product_type_summary" :
        if arguments == {}:
            return load_product_type_summary()
        else:
            raise ValueError("arguments must be empty")
    elif tool_name == "load_product_wear_summary":
        if arguments == {}:
            return load_product_wear_summary()
        else:
            raise ValueError("arguments must be empty")
    elif tool_name == "load_product_torque_summary":
        if arguments == {}:
            return load_product_torque_summary()
        else:
            raise ValueError("arguments must be empty")
    elif tool_name == "get_product_type_summary":
        if "product_type" not in arguments or len(arguments) != 1:
            raise ValueError("必须且只能提供 product_type 参数")
        if arguments["product_type"] not in ["L","H","M"]:
            raise ValueError("参数错误")
        return get_product_type_summary(arguments["product_type"])
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

        result = execute_tool(tool_name, arguments)
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





def get_product_type_summary(product_type: str) -> list[dict[str, str | int | float]]:
    if product_type not in ("L","H","M"):
        raise ValueError("没有该类产品")
    records=load_product_type_summary()
    for record in records:
        if record["product_type"] == product_type:
            return [record]
    return []



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
        max_retries=0,
        ) as client:
        try:
            answer = answer_question(client, question)
        except(OSError, sqlite3.Error, pd.errors.DatabaseError):
            print("数据库查询失败，请检查数据库和 SQL 文件")
            return
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
