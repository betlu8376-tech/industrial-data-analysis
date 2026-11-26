import argparse
import json
import os

from openai import OpenAI, APITimeoutError

from agent_demo import execute_tool
from rag_retriever import build_context, retrieve_evidence, rank_chunks


def route_question(question: str) -> str:
    text=question.strip().casefold()
    sql_keywords=("故障率","故障数","总记录数")
    rag_keywords=("手册","轴承","防冻","frost")
    has_sql = any(word in text for word in sql_keywords)
    has_rag = any(word in text for word in rag_keywords)
    if has_sql != has_rag:
        if has_sql==1:
            return "sql"
        else:
            return "rag"
    return "clarify"


def run_workflow(question, sql_handler, rag_handler):
    route=route_question(question)
    state = {
        "question": question,
        "route": route,
        "evidence": [],
    }

    if state["route"] == "sql":
        state["evidence"] = sql_handler(question)
    elif state["route"] == "rag":
        state["evidence"] = rag_handler(question)
    return state

def retrieve_sql_evidence(question: str) :
    question = question.strip().casefold()
    key_word="总体故障率"
    if key_word in question:
        return execute_tool("load_summary",{})
    return []


def build_workflow_messages(state):
    question = state["question"]
    route = state["route"]
    evidence = state["evidence"]
    if route == "sql":
        evidence_text=json.dumps(evidence)
    elif route == "rag":
        evidence_text=build_context(evidence)
    else:
        return []
    messages = [{"role":"system", "content":"要求根据证据回答，SQL 数值照实保留，引用手册时标明证据编号,只根据提供的证据回答，证据不足时明确说明"},
                {"role": "user", "content": f"问题\n{question}\n\n证据\n{evidence_text}"}]
    return messages


def answer_from_state(state,client):
    if state["route"] == "clarify":

        return "请说明你要查故障统计还是维护手册。"
    if not state["evidence"]:

        return "当前证据不足，无法回答这个问题。"
    messages = build_workflow_messages(state)
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        max_tokens=2048,
        extra_body={"thinking": {"type": "disabled"}}
    )
    return response.choices[0].message.content



def build_workflow_report(state, answer):
    if state["route"] == "sql":
        evidence=state["evidence"][0]
        evidence_text=f"总记录数:{evidence['total_count']} 故障数:{evidence['failure_count']} 故障率:{evidence['failure_rate_percent']}%"
    if state["route"] == "rag":
        evidence_text=""
        for number, hit in enumerate(state["evidence"], start=1):
            evidence_text+=f"[{number}] {hit['source_file']} 第 {hit['page']} 页\n"
    return f"question:{state['question']}\nevidence:{evidence_text}\nanswer:{answer}"



def main(question:str):
    state = run_workflow(question, retrieve_sql_evidence, retrieve_evidence)
    if not state["evidence"]:
        print(answer_from_state(state,None))
        return
    with OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )as client:
        try:
            answer = answer_from_state(state,client)
        except APITimeoutError:
            answer = "模型请求超时，暂时无法生成结论。以下是本次检索到的证据。"
        report=build_workflow_report(state,answer)
        print(report)







if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="询问问题")
    parser.add_argument(
        "question",
        type=str,
        help="要查询的问题"

    )
    args = parser.parse_args()
    main(question=args.question)


