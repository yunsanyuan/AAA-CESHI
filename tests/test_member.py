def test_member_center_ok_when_logged_in(member_session, base_url):
    page = member_session.get(f"{base_url}/member/", timeout=8, allow_redirects=False)
    assert page.status_code == 200
    assert "会员" in page.text


def test_member_profile_ok_when_logged_in(member_session, base_url, credentials):
    page = member_session.get(f"{base_url}/member/profile/", timeout=8, allow_redirects=False)
    assert page.status_code == 200
    assert "会员资料" in page.text
    assert credentials["username"] in page.text
