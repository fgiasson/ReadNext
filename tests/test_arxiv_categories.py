from readnext.arxiv_categories import exists

def test_exists():
    assert exists("cs") == True
    assert exists("cs.AI") == True
    assert exists("cs.ai") == False
    assert exists("cs.FOO") == False