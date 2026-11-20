from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from rag_loader import load_pdf_pages,split_pages

def test_load_pdf_pages_success(tmp_path:Path)->None:
    pdf_path = tmp_path/"grundfos_cr_en_2016_0616.pdf"

    page1=Mock()
    page1.extract_text.return_value = " 第一页正文 \n"
    page2=Mock()
    page2.extract_text.return_value = " 第二页正文 \n"
    fake_reader = Mock(pages=[page1, page2])
    with(
        patch("rag_loader.PdfReader", return_value=fake_reader)as mock_reader,
    ):
        result=load_pdf_pages(pdf_path,"test_id")
        mock_reader.assert_called_with(pdf_path)

        assert len(result) == 2
        for i in range(len(result)):
            assert result[i]["page"] == i + 1
            assert result[i]["document_id"] == "test_id"
            assert result[i]["source_file"] == pdf_path.name
        assert result[0]["text"] == "第一页正文"
        assert result[1]["text"] == "第二页正文"



def test_load_pdf_pages_preserves_empty_pages(tmp_path:Path)->None:
    pdf_path = tmp_path/"grundfos_cr_en_2016_0616.pdf"

    page1=Mock()
    page1.extract_text.return_value = " 开始 \n"
    page2=Mock()
    page2.extract_text.return_value = None
    page3=Mock()
    page3.extract_text.return_value = "\n\t"
    page4=Mock()
    page4.extract_text.return_value = " 结束 \n"
    fake_reader = Mock(pages=[page1, page2, page3, page4])
    with(
        patch("rag_loader.PdfReader", return_value=fake_reader)as mock_reader,
    ):
        result=load_pdf_pages(pdf_path, "test_id")
        mock_reader.assert_called_with(pdf_path)

        assert len(result) == 4
        for i in range(len(result)):
            assert result[i]["page"] == i+1
            assert result[i]["document_id"] == "test_id"
            assert result[i]["source_file"] == pdf_path.name
        assert result[0]["text"] == "开始"
        assert result[1]["text"] == ""
        assert result[2]["text"] == ""
        assert result[3]["text"] == "结束"

def test_split_pages_keeps_page_sources()->None:
    page19={"document_id":"test_id","source_file":"test_name","page":19,"text":"ABCDEFGHIJ"}
    page20={"document_id":"test_id","source_file":"test_name","page":20,"text":""}
    page21={"document_id":"test_id","source_file":"test_name","page":21,"text":"XYZ"}
    reader=[page19,page20,page21]
    chunks=split_pages(reader,5,2)
    assert [chunk["text"] for chunk in chunks]==["ABCDE", "DEFGH", "GHIJ", "XYZ"]
    assert [chunk["page"] for chunk in chunks] == [19, 19, 19, 21]
    assert [chunk["chunk_index"] for chunk in chunks] == [1, 2, 3, 1]
    assert all(chunk["document_id"] == "test_id" for chunk in chunks)
    assert all(chunk["source_file"] == "test_name" for chunk in chunks)



@pytest.mark.parametrize(
    "chunk_size,overlap",
    [(0,0),(-1,0),(5,-1),(5,5),(5,6)]
)
def test_split_pages_rejects_invalid_parameters(chunk_size,overlap)->None:
    page1=Mock()
    page2=Mock()
    reader=[page1,page2]
    with pytest.raises(ValueError, match="chunk_size > 0 and 0 <= overlap < chunk_size"):
        split_pages(reader,chunk_size,overlap)
