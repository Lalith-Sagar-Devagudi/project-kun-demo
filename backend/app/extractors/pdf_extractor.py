import pymupdf4llm
from langchain.text_splitter import MarkdownTextSplitter


def extract_pdf(pdf_path: list[str]) -> MarkdownTextSplitter:
    """Extracts the text content from a PDF file and splits it into chunks.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        MarkdownTextSplitter: The text splitter object.
    """
    md_content = ""
    # for all the pdf files in the pdf_path
    # extract the content and convert it to markdown
    for path in pdf_path:
        if path.endswith(".pdf"):
            md_content += pymupdf4llm.to_markdown(path)

    splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=0)

    docs = splitter.create_documents([md_content])

    # print(f"Extracted content: {docs}")

    return docs
