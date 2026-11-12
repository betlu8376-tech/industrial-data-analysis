import json
from unittest.mock import Mock, patch

from jsonschema.validators import create

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
        mock_execute_tool.assert_called_once_with("load_product_type_summary",{})
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
            execute_tool("unknown_tool",{})
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
        patch("agent_demo.load_product_type_summary") as mock_load,
    ):
        with pytest.raises(ValueError, match="arguments must be empty"):
            answer_question(client,"哪种产品故障率最高")
        mock_load.assert_not_called()
        client.chat.completions.create.assert_not_called()




@pytest.mark.parametrize("tool_name,expected_key",
                         [
                             ("load_product_type_summary", "product"),
                             ("load_product_wear_summary", "wear"),
                             ("load_product_torque_summary", "torque"),
                         ])
def test_execute_tool_success(tool_name:str,expected_key:str)->None:
    with(
        patch("agent_demo.load_product_type_summary") as mock_type,
        patch("agent_demo.load_product_wear_summary") as mock_wear,
        patch("agent_demo.load_product_torque_summary") as mock_torque,

    ):
        loaders = {
            "product": mock_type,
            "wear": mock_wear,
            "torque": mock_torque,
        }
        expected_loader = loaders[expected_key]
        result = execute_tool(tool_name,{})
        expected_loader.assert_called_once_with()
        assert result is expected_loader.return_value

        for key,loader in loaders.items():
            if key != expected_key:
                loaders[key].assert_not_called()


@pytest.mark.parametrize("product_type,expected_index",
                         [("L",0),("M",1),("H",2)])
def test_execute_tool_product_type_success(product_type:str,expected_index:int)->None:
    records=[
        {"product_type":"L","total_count":6000,"failure_count":235,"failure_rate_percent":3.92},
        {"product_type": "M", "total_count": 80, "failure_count": 40, "failure_rate_percent": 50.0},
        {"product_type": "H", "total_count": 6000, "failure_count": 2000, "failure_rate_percent": 33.33},
    ]
    with(
        patch("agent_demo.load_product_type_summary",return_value=records) as mock_load,
    ):
        result = execute_tool("get_product_type_summary",{"product_type":product_type})
        assert result == [records[expected_index]]
        mock_load.assert_called_once_with()



def test_execute_tool_product_type_empty()->None:
    records = [
        {"product_type": "L", "total_count": 6000, "failure_count": 235, "failure_rate_percent": 3.92},

        {"product_type": "H", "total_count": 6000, "failure_count": 2000, "failure_rate_percent": 33.33},
    ]
    with(
        patch("agent_demo.load_product_type_summary", return_value=records) as mock_load,
    ):
        result = execute_tool("get_product_type_summary",{"product_type":"M"})
        assert result == []
        mock_load.assert_called_once_with()

@pytest.mark.parametrize("arguments",
                         [[],{},{"product_type": "L", "extra": 1},{"product_type": "X"},{"product_type": 1}])
def test_execute_tool_product_type_rejects_arguments(arguments:dict[str, object])->None:
    records = [
        {"product_type": "L", "total_count": 6000, "failure_count": 235, "failure_rate_percent": 3.92},

        {"product_type": "H", "total_count": 6000, "failure_count": 2000, "failure_rate_percent": 33.33},
    ]
    with(
        patch("agent_demo.load_product_type_summary", return_value=records) as mock_load,
    ):
        with pytest.raises(ValueError):
            execute_tool("get_product_type_summary",arguments)
        mock_load.assert_not_called()



def test_answer_question_with_product_type()->None:
    client = Mock()

    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "L类型的故障率为 3.92%。"
    client.chat.completions.create.return_value = response

    tool_call = Mock(id="call_001")
    tool_call.function = Mock()
    tool_call.function.name = "get_product_type_summary"
    tool_call.function.arguments = '{"product_type": "L"}'
    message = Mock(tool_calls=[tool_call], content="你好，我可以帮助分析设备故障数据。")
    call_data = {
        "id": "call_001",
        "type": "function",
        "function": {
            "name": "get_product_type_summary",
            "arguments": '{"product_type": "L"}',
        }
    }
    message.model_dump.return_value = {"role": "assistant", "tool_calls": [call_data]}
    records = [
        {"product_type": "L", "total_count": 6000, "failure_count": 235, "failure_rate_percent": 3.92},
        {"product_type": "M", "total_count": 80, "failure_count": 40, "failure_rate_percent": 50.0},
        {"product_type": "H", "total_count": 6000, "failure_count": 2000, "failure_rate_percent": 33.33},
    ]

    with(
            patch("agent_demo.request_tool_call", return_value=message) as mock_request,
            patch("agent_demo.load_product_type_summary", return_value=records)as mock_load,

    ):
        result=answer_question(client, "只查询 L 类型产品的故障统计")
        assert result == "L类型的故障率为 3.92%。"
        mock_request.assert_called_once_with(client,"只查询 L 类型产品的故障统计")
        mock_load.assert_called_once_with()
        kwargs = client.chat.completions.create.call_args.kwargs
        sent_messages = kwargs["messages"]
        assert json.loads(sent_messages[2]["content"]) == [records[0]]
        client.chat.completions.create.assert_called_once()
