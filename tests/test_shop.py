def test_shop_list_returns_catalog(anon_session, base_url):
    page = anon_session.get(f"{base_url}/shop/", timeout=8)
    assert page.status_code == 200
    assert "花市" in page.text
    assert "在售" in page.text


def test_shop_detail_returns_product(anon_session, base_url, sample_product):
    page = anon_session.get(f"{base_url}/shop/{sample_product['id']}/", timeout=8)
    assert page.status_code == 200
    assert sample_product["name"] in page.text
    assert "加入购物车" in page.text or "售罄" in page.text
