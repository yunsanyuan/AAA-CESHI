from conftest import extract_csrf


def test_login_redirects_home_and_sets_session(anon_session, base_url, credentials):
    login_url = f"{base_url}/accounts/login/"
    page = anon_session.get(login_url, timeout=8)
    assert page.status_code == 200
    token = extract_csrf(page.text)

    posted = anon_session.post(
        login_url,
        data={
            "csrfmiddlewaretoken": token,
            "username": credentials["username"],
            "password": credentials["password"],
        },
        headers={"Referer": login_url},
        allow_redirects=False,
        timeout=8,
    )
    assert posted.status_code == 302
    assert posted.headers.get("Location") == "/"
    assert "sessionid" in anon_session.cookies


def test_login_missing_password_stays_on_form(anon_session, base_url, credentials):
    login_url = f"{base_url}/accounts/login/"
    page = anon_session.get(login_url, timeout=8)
    token = extract_csrf(page.text)

    posted = anon_session.post(
        login_url,
        data={
            "csrfmiddlewaretoken": token,
            "username": credentials["username"],
        },
        headers={"Referer": login_url},
        allow_redirects=False,
        timeout=8,
    )
    assert posted.status_code == 200
    assert "欢迎回来" in posted.text
    assert "登录" in posted.text
