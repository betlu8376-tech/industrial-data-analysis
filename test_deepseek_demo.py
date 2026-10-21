
from deepseek_demo import build_summary_prompt

from unittest.mock import Mock, patch, call

import openai
import pytest

from deepseek_demo import main,parse_retry_after_seconds


from run_sql2 import PROJECT_ROOT,DATABASE_PATH

import json
from pathlib import Path

from openai.types.completion_usage import CompletionUsage

from deepseek_demo import request_report

from openai import OpenAI, OpenAIError

from deepseek_demo import collect_stream_text,request_report_stream


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
        patch("deepseek_demo.time.sleep") as mock_sleep,

    ):
        main()

    output = capsys.readouterr().out
    assert "模型请求超时，请稍后重试。" in output
    assert client.chat.completions.create.call_count == 3

    assert mock_sleep.call_args_list == [call(1), call(2)]




@pytest.mark.parametrize(
    "token_usage",
    [CompletionUsage(
    prompt_tokens=120,
    completion_tokens=80,
    total_tokens=200,
),CompletionUsage(
    prompt_tokens=0,
    completion_tokens=0,
    total_tokens=0,
),None],
    ids=["normal_usage","zero_usage","missing_usage"]
)
def test_main_success(capsys: pytest.CaptureFixture[str],tmp_path:Path,token_usage:CompletionUsage | None) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,

    }]

    output_path = tmp_path / "model_failure_report.json"

    usage_log_path = tmp_path / "model_usage.jsonl"

    response=Mock()

    response.usage=token_usage

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
        patch("deepseek_demo.REPORT_PATH", output_path),
        patch("deepseek_demo.USAGE_LOG_PATH", usage_log_path),
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

    assert output_path.is_file()
    saved_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_data == report_data


    with usage_log_path.open("r",encoding="utf-8") as file:
        lines=file.read().splitlines()
        logs = [json.loads(line) for line in lines]
        assert len(logs)==1
        if token_usage:
            assert logs[0]["model"] == "glm-5.3-flash"
            assert logs[0]["prompt_tokens"] == token_usage.prompt_tokens
            assert logs[0]["completion_tokens"] == token_usage.completion_tokens
            assert logs[0]["total_tokens"] == token_usage.total_tokens
        else:
            assert logs[0]["model"] == "glm-5.3-flash"
            assert logs[0]["prompt_tokens"] is None
            assert logs[0]["completion_tokens"] is None
            assert logs[0]["total_tokens"] is None


    if token_usage:
        assert f"输入token：{token_usage.prompt_tokens}" in output
        assert f"输出token：{token_usage.completion_tokens}" in output
        assert f"消耗总量：{token_usage.total_tokens}" in output
    else:
        assert "token用量未返回" in output



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

    response.usage=None

    response.choices = [Mock()]
    response.choices[0].message.content = content


    client = Mock()
    client.chat.completions.create.return_value = response

    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),
        patch("deepseek_demo.append_usage_log") as mock_log,

    ):
        main()

    output = capsys.readouterr().out
    assert "模型未返回有效正文，请稍后重试。" in output
    client.chat.completions.create.assert_called_once()

    mock_log.assert_called_once()


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

    response.usage=None

    response.choices = [Mock()]
    response.choices[0].message.content = content


    client = Mock()
    client.chat.completions.create.return_value = response

    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),
        patch("deepseek_demo.save_report") as mock_save,
        patch("deepseek_demo.append_usage_log") as mock_log,

    ):
        main()

    output = capsys.readouterr().out
    assert output.strip().splitlines()[-1]=="报告格式或数据不合法"
    assert "这段结论不应输出" not in output
    client.chat.completions.create.assert_called_once()

    mock_save.assert_not_called()

    mock_log.assert_called_once()


def test_main_report_mismatch(capsys:pytest.CaptureFixture[str])-> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    response = Mock()

    response.usage=None

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
        patch("deepseek_demo.save_report") as mock_save,
        patch("deepseek_demo.append_usage_log") as mock_log,

    ):
        main()

    output = capsys.readouterr().out
    assert output.strip().splitlines()[-1] == "模型报告与查询结果不一致，请稍后重试。"
    assert "这份报告的结论不应输出" not in output
    client.chat.completions.create.assert_called_once()

    mock_save.assert_not_called()

    mock_log.assert_called_once()



@pytest.mark.parametrize(
    "save_error",
    [
        OSError("test disk write failed"),PermissionError("test write permission denied")
    ]
)
def test_main_handles_save_error(capsys: pytest.CaptureFixture[str],save_error)-> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    response = Mock()

    response.usage=None

    response.choices = [Mock()]
    response.choices[0].message.content = json.dumps({
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
        "conclusion": "总记录数为10000，故障数为339，故障率为3.39%。"
    },ensure_ascii=False)

    client = Mock()
    client.chat.completions.create.return_value = response
    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),
        patch(
            "deepseek_demo.save_report",
            side_effect=save_error,
        ) as mock_save,
        patch("deepseek_demo.append_usage_log",) as mock_log,

    ):
        main()

    output = capsys.readouterr().out
    assert output.strip().splitlines()[-1]=="报告保存失败，请检查输出路径或写入权限。"
    assert "总记录数为10000，故障数为339，故障率为3.39%。" not in output
    mock_save.assert_called_once()



def test_main_handles_usage_log_error(capsys: pytest.CaptureFixture[str],tmp_path:Path)-> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,

    }]

    output_path = tmp_path / "model_failure_report.json"

    usage_log_path = tmp_path / "model_usage.jsonl"

    response = Mock()

    response.usage = None

    response.choices = [Mock()]
    expexted_text = "总记录数为10000，故障数为339，故障率为3.39%。"
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
        patch("deepseek_demo.REPORT_PATH", output_path),
        patch("deepseek_demo.USAGE_LOG_PATH", usage_log_path),
        patch("deepseek_demo.append_usage_log",side_effect=OSError("test log write failed") )as mock_log,
    ):
        main()

    output = capsys.readouterr().out
    assert "用量日志保存失败，继续处理模型报告。" in output
    assert output_path.is_file()
    mock_log.assert_called_once()



def test_request_report_retries_then_succeeds():
    client = Mock()
    response = Mock()
    client.chat.completions.create.side_effect = [
        openai.APITimeoutError(request=Mock()),
        response,
    ]
    with patch("deepseek_demo.time.sleep") as mock_sleep:
        result = request_report(client, "测试提示词")

    assert result is response
    assert client.chat.completions.create.call_count == 2
    mock_sleep.assert_called_once_with(1)


@pytest.mark.parametrize(
    "error_class, status_code, expected_text",
    [
        (
            openai.AuthenticationError,
            401,
            "模型认证失败，请检查 API 密钥。",
        ),
        (
            openai.RateLimitError,
            429,
            "模型请求受限，请检查调用频率或账户额度。",
        ),
        (
            openai.BadRequestError,
            400,
            "模型请求失败，HTTP 状态码：400。",
        ),
    ],
    ids=["authentication", "rate_limit", "bad_request"],
)
def test_main_handles_api_status_error(capsys, error_class, status_code, expected_text) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    http_response = Mock(
        status_code=status_code,
        request=Mock(),
        headers={},
    )
    error = error_class(
        "test API failure",
        response=http_response,
        body=None,
    )
    client=Mock()
    client.chat.completions.create.side_effect=error
    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe)as mock_query,
        patch("deepseek_demo.save_report") as mock_save,
        patch("deepseek_demo.time.sleep") as mock_sleep,
        patch("deepseek_demo.append_usage_log") as mock_log,

    ):
        main()
        output = capsys.readouterr().out
        assert expected_text in output

        client.chat.completions.create.assert_called_once()
        mock_sleep.assert_not_called()
        mock_save.assert_not_called()
        mock_log.assert_not_called()



@pytest.mark.parametrize(
    "value, expected",
    [
        ("5", 5),
        (" 5 ", 5),
        ("0", 0),
        (None, None),
        ("", None),
        ("-1", None),
        ("1.5", None),
        ("abc", None),
        ("Wed, 21 Oct 2015 07:28:00 GMT", None),
    ],
)
def test_parse_retry_after_seconds(
    value: str | None,
    expected: int | None,
) -> None:
    result = parse_retry_after_seconds(value)
    assert result == expected



@pytest.mark.parametrize(
    "retry_after, expected_text",
    [
        ("5", "服务端建议至少等待 5 秒后再尝试"),
        ("0", "服务端建议至少等待 0 秒后再尝试"),
        (None, "模型请求受限，请检查调用频率或账户额度。"),
        ("abc", "模型请求受限，请检查调用频率或账户额度。"),
    ],
    ids=["seconds", "zero", "missing", "invalid"],
)
def test_main_handles_retry_after(capsys: pytest.CaptureFixture[str],retry_after: str | None,expected_text: str) -> None:
    dataframe = Mock()
    dataframe.to_dict.return_value = [{
        "total_count": 10000,
        "failure_count": 339,
        "failure_rate_percent": 3.39,
    }]

    headers = {}
    if retry_after is not None:
        headers["retry-after"] = retry_after

    http_response = Mock(
        status_code=429,
        request=Mock(),
        headers=headers,
    )

    error = openai.RateLimitError(
        "test rate limit",
        response=http_response,
        body=None,
    )
    client=Mock()
    client.chat.completions.create.side_effect=error
    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe)as mock_query,
        patch("deepseek_demo.save_report") as mock_save,
        patch("deepseek_demo.time.sleep") as mock_sleep,
        patch("deepseek_demo.append_usage_log") as mock_log,

    ):
        main()
        output = capsys.readouterr().out
        assert expected_text in output

        client.chat.completions.create.assert_called_once()
        mock_sleep.assert_not_called()
        mock_save.assert_not_called()
        mock_log.assert_not_called()


def test_collect_stream_text(capsys: pytest.CaptureFixture[str]) -> None:
    chunks = [
        Mock(choices=[]),
        Mock(choices=[Mock(delta=Mock(content=None))]),
        Mock(choices=[Mock(delta=Mock(content="总记录数"))]),
        Mock(choices=[Mock(delta=Mock(content=""))]),
        Mock(choices=[Mock(delta=Mock(content="为10000，"))]),
        Mock(choices=[Mock(delta=Mock(content="故障率为3.39%。"))]),
    ]

    result = collect_stream_text(chunks)

    expected = "总记录数为10000，故障率为3.39%。"

    assert result == expected
    assert capsys.readouterr().out == expected



def test_collect_stream_text_empty(
    capsys: pytest.CaptureFixture[str],
) -> None:
    chunks = [
        Mock(choices=[]),

        Mock(choices=[Mock(delta=Mock(content=""))]),
    ]
    result = collect_stream_text(chunks)
    expected = ""
    assert result == expected
    assert capsys.readouterr().out == expected


def test_request_report_stream_success() -> None:
    client = Mock()
    stream = Mock()
    client.chat.completions.create.return_value = stream

    with patch(
        "deepseek_demo.collect_stream_text",
        return_value="测试正文",
    ) as mock_collect:
        result = request_report_stream(client, "测试提示词")

    assert result == "测试正文"
    mock_collect.assert_called_once_with(stream)
    stream.close.assert_called_once()

    client.chat.completions.create.assert_called_once()
    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs["stream"] is True
    assert kwargs["messages"] == [
        {"role": "user", "content": "测试提示词"},
    ]


def test_request_report_stream_closes_on_error()-> None:
    client = Mock()
    stream = Mock()
    client.chat.completions.create.return_value = stream

    with patch("deepseek_demo.collect_stream_text",side_effect=RuntimeError("读取流失败")) as mock_collect:
        with pytest.raises(RuntimeError,match="读取流失败"):
            request_report_stream(client, "测试提示词")

    mock_collect.assert_called_once_with(stream)
    stream.close.assert_called_once()
    client.chat.completions.create.assert_called_once()
