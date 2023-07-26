from readnext.embedding import pdf_to_text, get_pdfs_from_folder

def test_pdf_to_text():
    assert pdf_to_text("tests/assets/test.pdf") == "this is a test"
    assert pdf_to_text("tests/assets/test.pdf") != "this is a test foo"

def test_get_pdfs_from_folder():
    assert get_pdfs_from_folder("tests/assets/") == ['test.pdf']
    assert get_pdfs_from_folder("tests/assets/") != ['test.pdf', 'foo.pdf']

def test_embed_category_papers():
    pass

