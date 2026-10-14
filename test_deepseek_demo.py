from _pytest import monkeypatch
from matplotlib.font_manager import json_dump

from deepseek_demo import build_summary_prompt

from unittest.mock import Mock, patch

import openai
import pytest

from deepseek_demo import main


from run_sql2 import PROJECT_ROOT,DATABASE_PATH

from report_schema import FailureReport
from pydantic import ValidationError
import json


def test_build_summary_prompt() -> None:
    summary = {
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }

    prompt = build_summary_prompt(summary)

    assert "总记录数为 10000" in prompt
    assert "故障数为 339" in prompt
    assert "故障率为 3.39%" in prompt
    assert "不要推测故障原因" in prompt
    assert "只返回一个合法的 JSON 对象" in prompt
    assert "不要 Markdown 代码围栏或额外说明" in prompt
    for field_name in (
        "total_count", "failure_count", "failure_rate_percent", "conclusion"
    ):
        assert f'"{field_name}"' in prompt


def test_build_summary_prompt_with_different_data() -> None:
    summary = {
        "total_count": 200,
        "failure_count": 10,
        "failure_rate_percent": 5.0,
    }

    prompt = build_summary_prompt(summary)

    assert "总记录数为 200" in prompt
    assert "故障数为 10" in prompt
    assert "故障率为 5.0%" in prompt
    assert "不要推测故障原因" in prompt
    assert "只返回一个合法的 JSON 对象" in prompt
    assert "不要 Markdown 代码围栏或额外说明" in prompt
    for field_name in (
        "total_count", "failure_count", "failure_rate_percent", "conclusion"
    ):
        assert f'"{field_name}"' in prompt

def test_main_handles_timeout(capsys: pytest.CaptureFixture[str]) -> None:
    """模拟请求超时，检查程序是否提示并退出。"""
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    client = Mock()
    client.chat.completions.create.side_effect = (
        openai.APITimeoutError(request=Mock())
    )

    with (
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),
        patch("deepseek_demo.OpenAI", return_value=client),
    ):
        main()

    output = capsys.readouterr().out
    assert "模型请求超时，请稍后重试。" in output
    client.chat.completions.create.assert_called_once()


def test_main_success(capsys: pytest.CaptureFixture[str]) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,

    }]

    response=Mock()
    response.choices = [Mock()]
    expexted_text="总记录数为10000，故障数为339，故障率为3.39%。"
    report_data = {
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
        "conclusion": "总记录数为10000，故障数为339，故障率为3.39%。"
    }
    response.choices[0].message.content = json.dumps(
        report_data, ensure_ascii=False
    )

    client = Mock()
    client.chat.completions.create.return_value = response

    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe) as mock_query,
    ):
        main()
    output = capsys.readouterr().out
    assert expexted_text in output
    client.chat.completions.create.assert_called_once()

    request_kwargs = client.chat.completions.create.call_args.kwargs
    assert request_kwargs["model"] =="glm-5.3-flash"
    assert request_kwargs["max_tokens"] ==2048

    message = request_kwargs["messages"]
    assert len(message)==1
    assert message[0]["role"] == "user"

    expexted_summary=dataframe.to_dict.return_value[0]
    expected_prompt=build_summary_prompt(expexted_summary)
    assert message[0]["content"] == expected_prompt


    expexted_sql_path=PROJECT_ROOT / "sql" / "01_failure_summary.sql"
    mock_query.assert_called_once_with(DATABASE_PATH,expexted_sql_path)
    mock_query.assert_called_once()


    assert output.strip().splitlines()[-1] == expexted_text



def test_main_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    monkeypatch.delenv("ZHIPU_API_KEY",raising=False)
    with(
        patch("deepseek_demo.execute_query", return_value=dataframe),
        patch("deepseek_demo.OpenAI")as mock_openai

    ):


        with pytest.raises(RuntimeError,match="ZHIPU_API_KEY is not configured"):
            main()

        mock_openai.assert_not_called()



@pytest.mark.parametrize(
        "content",
        ["",None,"   "],
        ids=["empty","none","whitespace"]
    )
def test_main_invalid_content(capsys: pytest.CaptureFixture[str], content: str | None ) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    response=Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = content


    client = Mock()
    client.chat.completions.create.return_value = response

    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),

    ):
        main()

    output = capsys.readouterr().out
    assert "模型未返回有效正文，请稍后重试。" in output
    client.chat.completions.create.assert_called_once()


def test_main_query_failure()-> None:
    client = Mock()

    with(
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", side_effect=FileNotFoundError("SQL file missing for test"))as mock_query,
        patch("deepseek_demo.OpenAI", return_value=client)as mock_openai,
    ):
        with pytest.raises(FileNotFoundError,match="SQL file missing for test"):
            main()

    mock_query.assert_called_once()
    mock_openai.assert_not_called()



@pytest.mark.parametrize(
    "content",
    [   "这不是json",
        json.dumps({
        "total_count": 100,
        "failure_count": 30,
        "failure_rate_percent": 60,
        "conclusion": "这段结论不应输出"
    },ensure_ascii=False)],
    ids=["not json","inconsistent_rate"]
)
def test_main_invalid_report(capsys: pytest.CaptureFixture[str], content: str | None ) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    response=Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = content


    client = Mock()
    client.chat.completions.create.return_value = response

    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),

    ):
        main()

    output = capsys.readouterr().out
    assert output.strip().splitlines()[-1]=="报告格式或数据不合法"
    assert "这段结论不应输出" not in output
    client.chat.completions.create.assert_called_once()


def test_main_report_mismatch(capsys:pytest.CaptureFixture[str])-> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = json.dumps({
        "total_count": 100,
        "failure_count": 10,
        "failure_rate_percent": 10,
        "conclusion": "这份报告的结论不应输出"
    },ensure_ascii=False)

    client = Mock()
    client.chat.completions.create.return_value = response
    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),

    ):
        main()

    output = capsys.readouterr().out
    assert output.strip().splitlines()[-1] == "模型报告与查询结果不一致，请稍后重试。"
    assert "这份报告的结论不应输出" not in output
    client.chat.completions.create.assert_called_once()


