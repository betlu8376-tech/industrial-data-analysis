from _pytest import monkeypatch

from deepseek_demo import build_summary_prompt

from unittest.mock import Mock, patch

import openai
import pytest

from deepseek_demo import main


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
    response.choices[0].message.content = expexted_text

    client = Mock()
    client.chat.completions.create.return_value = response

    with (
        patch("deepseek_demo.OpenAI", return_value=client),
        patch.dict("os.environ", {"ZHIPU_API_KEY": "test-placeholder"}),
        patch("deepseek_demo.execute_query", return_value=dataframe),
    ):
        main()
    output = capsys.readouterr().out
    assert expexted_text in output
    client.chat.completions.creatassert_called_once()

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