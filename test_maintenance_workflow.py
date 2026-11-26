from unittest.mock import Mock, patch

import pytest

from maintenance_workflow import *




@pytest.mark.parametrize(
    "question,expected_route",
    [("故障率&*^&故障数","sql"),("手册$%防冻","rag"),("故障率&&手册$","clarify"),("121212","clarify"),("","clarify"),("FROST","rag")],
)
def test_route_question_parameter(question, expected_route):
    assert route_question(question) == expected_route


def test_workflow_sql():
    sql_rows = [{"product_type": "L", "failure_rate_percent": 3.92}]
    rag_hits = [{"source_file": "abb.pdf", "page": 19, "text": "测试片段"}]

    sql_handler = Mock(return_value=sql_rows)
    rag_handler = Mock(return_value=rag_hits)

    question="L 型产品的故障率是多少？"
    state=run_workflow(question, sql_handler, rag_handler)
    assert state["question"] == question
    assert state["route"] == "sql"
    assert state["evidence"] == sql_rows
    sql_handler.assert_called_once_with(question)
    rag_handler.assert_not_called()

def test_workflow_rag():
    sql_rows = [{"product_type": "L", "failure_rate_percent": 3.92}]
    rag_hits = [{"source_file": "abb.pdf", "page": 19, "text": "测试片段"}]

    sql_handler = Mock(return_value=sql_rows)
    rag_handler = Mock(return_value=rag_hits)

    question="ABB 电机怎么检查轴承状态？"
    state=run_workflow(question, sql_handler, rag_handler)
    assert state["question"] == question
    assert state["route"] == "rag"
    assert state["evidence"] == rag_hits
    rag_handler.assert_called_once_with(question)
    sql_handler.assert_not_called()

def test_workflow_clarify():
    sql_rows = [{"product_type": "L", "failure_rate_percent": 3.92}]
    rag_hits = [{"source_file": "abb.pdf", "page": 19, "text": "测试片段"}]

    sql_handler = Mock(return_value=sql_rows)
    rag_handler = Mock(return_value=rag_hits)

    question="今天天气如何？"
    state=run_workflow(question, sql_handler, rag_handler)
    assert state["question"] == question
    assert state["route"] == "clarify"
    assert state["evidence"] == []
    sql_handler.assert_not_called()
    rag_handler.assert_not_called()

@pytest.mark.parametrize(
    "state",
    [{"question":"test_question","route": "rag", "evidence": [{"source_file":"test_file","page":212,"text":"test_text"}]},
     {"question":"test_question","route": "sql", "evidence": [{"failure_rate_percent": 3.92}]},
     {"question":"test_question","route":"clarify", "evidence":[]},
     {"question":"test_question","route": "rag", "evidence": []}]
)
def test_answer_from_state(state):
    client= Mock()

    content="mock_content"
    message=Mock(content=content)
    choice=Mock(message=message)
    client.chat.completions.create.return_value = Mock(choices=[choice])
    result = answer_from_state(state,client)
    if state["route"] == "rag":
        if state["evidence"]:
            assert result == "mock_content"
            client.chat.completions.create.assert_called_once()
        else:
            assert result == "当前证据不足，无法回答这个问题。"
            client.chat.completions.create.assert_not_called()
    if state["route"] == "sql":
        assert result == "mock_content"
        client.chat.completions.create.assert_called_once()
    if state["route"] == "clarify":
        assert result == "请说明你要查故障统计还是维护手册。"
        client.chat.completions.create.assert_not_called()

def test_main(capsys):
    chunk1={"source_file":"abb.pdf","page":19,"text":"chunk19"}
    chunk2={"source_file":"abb.pdf","page":7,"text":"chunk7"}
    hits=[chunk1,chunk2]
    question="ABB 电机怎么检查轴承状态？"
    with(
        patch("maintenance_workflow.retrieve_evidence", return_value=hits)as mock_retrieve,
        patch("maintenance_workflow.OpenAI")as mock_openai,
        patch("maintenance_workflow.answer_from_state",return_value="可以检查振动和温度 [1]")as mock_answer,
    ):
        main(question)
        mock_retrieve.assert_called_once_with(question)
        output = capsys.readouterr().out
        assert "[1] abb.pdf 第 19 页" in output
        assert "[2] abb.pdf 第 7 页" in output
        assert "可以检查振动和温度 [1]" in output
        expected_state = {"question": question, "route": "rag", "evidence": hits}
        client = mock_openai.return_value.__enter__.return_value
        mock_answer.assert_called_once_with(expected_state, client)


def test_main_timeout(capsys):
    chunk1 = {"source_file": "abb.pdf", "page": 19, "text": "chunk19"}
    chunk2 = {"source_file": "abb.pdf", "page": 7, "text": "chunk7"}
    hits = [chunk1, chunk2]
    question = "ABB 电机怎么检查轴承状态？"
    with(
        patch("maintenance_workflow.retrieve_evidence", return_value=hits) as mock_retrieve,
        patch("maintenance_workflow.OpenAI") as mock_openai,
    ):
        client = mock_openai.return_value.__enter__.return_value
        client.chat.completions.create.side_effect = APITimeoutError(request=Mock())
        main(question)
        output = capsys.readouterr().out
        mock_retrieve.assert_called_once_with(question)
        assert "模型请求超时，暂时无法生成结论。以下是本次检索到的证据。" in output
        assert "[1] abb.pdf 第 19 页" in output
        assert "[2] abb.pdf 第 7 页" in output