import os
from readnext.arxiv_sync import get_arxiv_pdfs_url, get_docs_path, delete_broken_pdf

def test_get_arxiv_pdfs_url():
    # valid
    assert len(get_arxiv_pdfs_url("cs")) > 0
    assert len(get_arxiv_pdfs_url("cs.AI")) > 0

    # invalid
    assert len(get_arxiv_pdfs_url("cs.ai")) == 0
    assert len(get_arxiv_pdfs_url("cs.FOO")) == 0


def test_get_docs_path():
    assert get_docs_path("cs") == os.environ.get('DOCS_PATH').rstrip('/') + '/' + "cs" + '/'
    assert get_docs_path("cs.AI") == os.environ.get('DOCS_PATH').rstrip('/') + '/' + "cs.AI" + '/'
    assert get_docs_path("cs.FOO") != os.environ.get('DOCS_PATH').rstrip('/') + '/' + "cs.AI" + '/'


def test_delete_broken_pdf():
    # count the current number of PDF files in docs_path
    docs_path = get_docs_path("cs")
    os.makedirs(docs_path, exist_ok=True)
    pdf_files = os.listdir(docs_path)
    pdf_files_count_before = len(pdf_files)
    
    # create and empty PDF file at docs_path to produce an invalid PDF file
    docs_path = get_docs_path("cs")
    open(docs_path + "foo.pdf", 'a').close()

    # run delete_broken_pdf
    delete_broken_pdf("cs")

    # count the number of PDF files in docs_path
    pdf_files = os.listdir(docs_path)
    pdf_files_count_after = len(pdf_files)

    assert pdf_files_count_after == pdf_files_count_before

def test_sync_arxiv():
    pass

