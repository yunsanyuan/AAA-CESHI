from conftest import extract_csrf


def test_add_to_cart_then_see_item(member_session, base_url, sample_product):
    detail_url = f"{base_url}/shop/{sample_product['id']}/"
    detail = member_session.get(detail_url, timeout=8)
    assert detail.status_code == 200
    token = extract_csrf(detail.text)

    posted = member_session.post(
        f"{base_url}/shop/{sample_product['id']}/add/",
        data={
            "csrfmiddlewaretoken": token,
            "quantity": "1",
            "next": "/orders/cart/",
        },
        headers={"Referer": detail_url},
        allow_redirects=False,
        timeout=8,
    )
    assert posted.status_code == 302
    assert "/orders/cart/" in posted.headers.get("Location", "")

    cart = member_session.get(f"{base_url}/orders/cart/", timeout=8)
    assert cart.status_code == 200
    assert "购物车" in cart.text
    assert sample_product["name"] in cart.text
