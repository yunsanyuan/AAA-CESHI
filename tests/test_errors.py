def test_unknown_product_is_404(anon_session, base_url):
    page = anon_session.get(f"{base_url}/shop/999999/", timeout=8)
    assert page.status_code == 404


def test_member_center_requires_login(anon_session, base_url):
    page = anon_session.get(f"{base_url}/member/", timeout=8, allow_redirects=False)
    assert page.status_code == 302
    location = page.headers.get("Location", "")
    assert "/accounts/login/" in location


def test_fake_session_cookie_cannot_open_member_center(anon_session, base_url):
    anon_session.cookies.set("sessionid", "not-a-real-session")
    page = anon_session.get(f"{base_url}/member/", timeout=8, allow_redirects=False)
    assert page.status_code == 302
    assert "/accounts/login/" in page.headers.get("Location", "")


def test_add_cart_without_csrf_is_forbidden(member_session, base_url, sample_product):
    posted = member_session.post(
        f"{base_url}/shop/{sample_product['id']}/add/",
        data={"quantity": "1", "next": "/orders/cart/"},
        headers={"Referer": f"{base_url}/shop/{sample_product['id']}/"},
        allow_redirects=False,
        timeout=8,
    )
    assert posted.status_code == 403
