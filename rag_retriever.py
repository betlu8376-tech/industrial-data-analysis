import argparse
import os
from  math import ceil,sqrt
from pathlib import Path

from fastembed import TextEmbedding
from openai import OpenAI
from typing_extensions import final

from rag_loader import load_pdf_pages, split_pages, embed_chunks


def rank_chunks(query_vector, chunks, top_k=3):
    scored_chunks = []
    query_norm = sqrt(sum(value ** 2 for value in query_vector))
    if type(top_k) != int or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")
    if query_norm <=0 :
        raise ValueError("query_norm and top_k must be positive")
    for chunk in chunks:
        vector=chunk["embedding"]
        dis=len(vector)
        if len(vector) != len(query_vector):
            raise ValueError("向量维度不一致")
        dis_norm = sqrt(sum(value ** 2 for value in vector))
        dot_product = sum(a * b for a, b in zip(query_vector, vector))
        if dis_norm <= 0:
            raise ValueError("dis_norm must be positive")
        score = dot_product / (query_norm*dis_norm)
        hit=chunk.copy()
        hit["score"]=score
        scored_chunks.append(hit)
    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return scored_chunks[:top_k]



def build_context(hits):
    number=0
    blocks=[]
    for hit in hits:
        number+=1
        context=f"[{number}] {hit['source_file']} 第 {hit['page']} 页\n{hit['text']}"
        blocks.append(context)
    return "\n\n".join(blocks)



def answer_with_context(client:OpenAI, question, hits):
    if not hits:
        return "现有手册片段无法回答这个问题"
    message=[{"role":"user","content": f"问题\n{question}\n\n手册证据\n{build_context(hits)}"},
             {"role":"system","content":"根据给定证据回答，在结论后标注证据编号。如果证据不足，就说「现有手册片段无法回答这个问题」"}]

    final_response=client.chat.completions.create(
        model="deepseek-flash",
        messages=message,
        max_tokens=2048,
        extra_body={"thinking": {"type": "disabled"}}
    )


    return final_response.choices[0].message.content

def retrieve_evidence(question:str):
    model = TextEmbedding("BAAI/bge-small-zh-v1.5")

    pdf_path1 = Path(__file__).resolve().parent / "data/knowledge/manuals/abb_lv_motors_3gzf500730_85_rev_h_2022_zh.pdf"
    abb_pages = load_pdf_pages(pdf_path1, "abb_lv_motors_zh_2022_h")

    pdf_path2 = Path(__file__).resolve().parent / "data/knowledge/manuals/grundfos_cr_cri_crn_96462123_0616_en.pdf"
    grundfos_pages = load_pdf_pages(pdf_path2, "grundfos_cr_en_2016_0616")

    pages = abb_pages + grundfos_pages
    chunks = split_pages(pages, 512, 128)
    embedding_chunks = embed_chunks(model, chunks)

    query_vector = next(model.embed([question])).tolist()
    result = rank_chunks(query_vector, embedding_chunks, top_k=3)
    return result

def main(question:str):
    question = question.strip()
    if not question:
        print("问题不能为空")
        return

    result = retrieve_evidence(question)

    with OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
    ) as client:
        response = answer_with_context(client, question, result)
    for number,hit in enumerate(result,start=1):
        print(f"[{number}] {hit['source_file']} 第 {hit['page']} 页")

    print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="询问问题")
    parser.add_argument(
        "question",
        type=str,
        help="要查询的 ABB 手册问题"

    )
    args = parser.parse_args()
    main(question=args.question)


