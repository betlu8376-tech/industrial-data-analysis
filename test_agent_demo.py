import json
from unittest.mock import Mock, patch

from agent_demo import request_tool_call,tools,answer_question,execute_tool


import pytest


def test_request_tool_call_success():
    client = Mock()
    message=Mock()
    response = Mock()
    response.choices = [Mock(message=message)]
    client.chat.completions.create.return_value = response

    result=request_tool_call(client,"哪种产品故障率最高")
    assert result is message

    client.chat.completions.create.assert_called_once()
    kwargs = client.chat.completions.create.call_args.kwargs

    assert kwargs["max_tokens"] == 2048
    assert kwargs["messages"] ==[{"role": "user", "content": "哪种产品故障率最高"}]

    assert kwargs["tools"] == tools
    assert kwargs["tool_choice"] == "auto"



def test_answer_question_without_tools()->None:
    client = Mock()
    message=Mock(tool_calls=[],content="你好，我可以帮助分析设备故障数据。")

    with(
        patch("agent_demo.request_tool_call", return_value=message)as mock_request,
        patch("agent_demo.execute_tool")as mock_execute_tool,
    ):
        result=answer_question(client,"哪种产品故障率最高")
        mock_request.assert_called_once_with(client, "哪种产品故障率最高")
        client.chat.completions.create.assert_not_called()

        assert result == "你好，我可以帮助分析设备故障数据。"
        mock_execute_tool.assert_not_called()


def test_answer_question_with_tool()->None:
    client = Mock()

    response=Mock()
    response.choices = [Mock()]
    response.choices[0].message.content="L 类型的故障率最高，为 3.92%。"
    client.chat.completions.create.return_value = response

    tool_call = Mock(id="call_001")
    tool_call.function = Mock()
    tool_call.function.name = "load_product_type_summary"
    tool_call.function.arguments = "{}"
    message = Mock(tool_calls=[tool_call],content="你好，我可以帮助分析设备故障数据。")
    call_data={
                "id": "call_001",
                "type":"function",
                "function":{
                            "name": "load_product_type_summary",
                            "arguments": "{}",
                }
    }
    message.model_dump.return_value={"role":"assistant","tool_calls":[call_data]}
    loaded_data=[{"product_type": "L", "total_count": 6000, "failure_count": 235, "failure_rate_percent": 3.92}]

    with(
        patch("agent_demo.request_tool_call", return_value=message) as mock_request,
        patch("agent_demo.execute_tool",return_value=loaded_data) as mock_execute_tool,
    ):
        result = answer_question(client, "哪种产品故障率最高")


        mock_request.assert_called_once_with(client, "哪种产品故障率最高")
        client.chat.completions.create.assert_called_once()
        mock_execute_tool.assert_called_once_with("load_product_type_summary")
        assert result==response.choices[0].message.content

        kwargs = client.chat.completions.create.call_args.kwargs
        sent_messages = kwargs["messages"]
        assert len(sent_messages) == 3
        assert sent_messages[0]["role"] == "user"
        assert sent_messages[0]["content"]=="哪种产品故障率最高"
        assert sent_messages[1]["role"] == "assistant"
        assert sent_messages[1]["tool_calls"] == [call_data]
        assert sent_messages[2]["role"] == "tool"
        assert json.loads(sent_messages[2]["content"]) == loaded_data
        assert sent_messages[2]["tool_call_id"] == "call_001"


def test_execute_tool_rejects_unknown_name()->None:
    with(
        patch("agent_demo.load_product_type_summary") as mock_load,
    ):
        with pytest.raises(ValueError, match="未知工具"):
            execute_tool("unknown_tool")
            mock_load.assert_not_called()


def test_answer_question_rejects_arguments()->None:
    client = Mock()

    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "L 类型的故障率最高，为 3.92%。"
    client.chat.completions.create.return_value = response

    tool_call = Mock(id="call_001")
    tool_call.function = Mock()
    tool_call.function.name = "load_product_type_summary"
    tool_call.function.arguments = '{"product_type": "L"}'
    message = Mock(tool_calls=[tool_call], content="你好，我可以帮助分析设备故障数据。")
    call_data = {
        "id": "call_001",
        "type": "function",
        "function": {
            "name": "load_product_type_summary",
            "arguments": '{"product_type": "L"}',
        }
    }
    message.model_dump.return_value = {"role": "assistant", "tool_calls": [call_data]}

    with(
        patch("agent_demo.request_tool_call", return_value=message) as mock_request,
        patch("agent_demo.execute_tool") as mock_execute_tool,
    ):
        with pytest.raises(ValueError, match="该调用不应有参数"):
            answer_question(client,"哪种产品故障率最高")
        mock_execute_tool.assert_not_called()
        client.chat.completions.create.assert_not_called()