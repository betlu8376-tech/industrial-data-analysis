from pathlib import Path

from pypdf import PdfReader






def load_pdf_pages(pdf_path: Path, document_id: str) -> list[dict[str, str | int]]:
    reader = PdfReader(pdf_path)
    result = list()
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        need={"document_id":document_id,"source_file":pdf_path.name,"page":page_number,"text":text}
        result.append(need)
    return result


def split_pages(pages, chunk_size=500, overlap=80):
    result = []
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size > 0 and 0 <= overlap < chunk_size")
    for page in pages:
        if page["text"] is None:
            continue
        start = 0
        chunk_index = 1
        text = page["text"]
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            chunk={"document_id":page["document_id"],"source_file":page["source_file"],"page":page["page"],"text":chunk_text,"chunk_index":chunk_index}
            result.append(chunk)
            if end == len(text):
                break
            start += chunk_size - overlap
            chunk_index += 1
    return result

def embed_chunks(model, chunks)->list[dict[str, str | int | list[float]]]:
    result = []
    texts = [chunk["text"] for chunk in chunks]
    vectors = model.embed(texts, batch_size=8)
    for chunk, vector in zip(chunks, vectors,strict=True):
        chunk=chunk.copy()
        chunk["embedding"] = vector.tolist()
        result.append(chunk)
    return result



if __name__ == "__main__":
    pdf_path = Path(
        r"D:\Documents\ChatGPT\PythonProject\data\knowledge\manuals\grundfos_cr_cri_crn_96462123_0616_en.pdf")
    result = load_pdf_pages(pdf_path, "grundfos_cr_en_2016_0616")
    print(result)