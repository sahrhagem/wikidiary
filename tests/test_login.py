from wikidiary import Wiki

def test_login():
    wiki = Wiki()
    assert wiki.get_csrf_token() 