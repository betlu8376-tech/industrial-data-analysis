from unittest.mock import Mock

import pytest
from openai import OpenAI

from rag_retriever import rank_chunks,answer_with_context





def test_rank_chunks_returns_top_k():
    chunk3={"embedding": [0,1],"page":3}
    chunk12={"embedding": [4,3],"page":12}
    chunk19={"embedding": [1,0],"page":19}
    chunks=[chunk3,chunk12,chunk19]
    hits=rank_chunks([1,0],chunks,2)
    assert [hit["score"] for hit in hits] == pytest.approx([1.0, 0.8])
    assert [hit["page"] for hit in hits] == [19,12]

@pytest.mark.parametrize(
    "query_vector, chunks,top_k",
    [([1,0],[{"embedding":[0,1]}],1.5),([0,0],[{"embedding":[0,1]}],1),([1,0],[{"embedding":[0,0]}],2),([1,0],[{"embedding":[0,0,1]}],2)]
)
def test_rank_chunks_rejects_invalid_inputs(query_vector, chunks, top_k):
    with pytest.raises(ValueError):
        rank_chunks(query_vector, chunks, top_k)


def test_answer_with_context_hits_empty():
    client = Mock()
    outputs=answer_with_context(client,"test_question",[])
    assert outputs =="现有手册片段无法回答这个问题"
    client.chat.completions.create.assert_not_called()


def test_answer_with_context_hits():
    client = Mock()
    reply = Mock(content="test_response")
    choice = Mock(message=reply)
    client.chat.completions.create.return_value = Mock(choices=[choice])

    hits=[{"source_file":"abb.pdf","page":19,"text":"test_text"}]
    question = "test_question"
    response = answer_with_context(client,question,hits)
    assert response=="test_response"
    client.chat.completions.create.assert_called_once()
    create = client.chat.completions.create
    messages = create.call_args.kwargs["messages"]

    user_message=next(msg for msg in messages if msg["role"] == "user")
    content=user_message["content"]
    hit = hits[0]

    assert question in content
    assert hit["source_file"] in content
    assert f"第 {hit['page']} 页" in content
    assert hit["text"] in content



