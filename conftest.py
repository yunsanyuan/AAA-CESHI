import os
import re
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

_CSRF_PATTERNS = (
    re.compile(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']'),
    re.compile(r'value=["\']([^"\']+)["\']\s+name=["\']csrfmiddlewaretoken["\']'),
)
_PRODUCT_HREF = re.compile(r'href=["\']/shop/(\d+)/["\']')


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "http: black-box HTTP tests against a running runserver",
    )


def extract_csrf(html: str) -> str:
    for pattern in _CSRF_PATTERNS:
        match = pattern.search(html)
        if match:
            return match.group(1)
    raise AssertionError("页面里没有 csrfmiddlewaretoken，请确认打开的是 Django 表单页")


@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        requests.get(url, timeout=5)
    except requests.RequestException as exc:
        pytest.exit(
            f"连不上 {url}。请先启动花间集："
            "https://github.com/yunsanyuan/sanyuan  "
            "python manage.py seed_demo && python manage.py runserver\n"
            f"原错误：{exc}",
            returncode=1,
        )
    return url


@pytest.fixture
def anon_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "AAA-CESHI pytest"})
    return session


@pytest.fixture(scope="session")
def credentials():
    return {
        "username": os.getenv("DEMO_USER", "demo_member"),
        "password": os.getenv("DEMO_PASSWORD", "member123456"),
    }


@pytest.fixture
def member_session(base_url, credentials):
    session = requests.Session()
    session.headers.update({"User-Agent": "AAA-CESHI pytest"})
    login_page = session.get(f"{base_url}/accounts/login/", timeout=8)
    assert login_page.status_code == 200, f"打不开登录页：{login_page.status_code}"
    token = extract_csrf(login_page.text)
    posted = session.post(
        f"{base_url}/accounts/login/",
        data={
            "csrfmiddlewaretoken": token,
            "username": credentials["username"],
            "password": credentials["password"],
        },
        headers={"Referer": f"{base_url}/accounts/login/"},
        allow_redirects=False,
        timeout=8,
    )
    assert posted.status_code == 302, (
        f"登录失败，期望 302，实际 {posted.status_code}。"
        "请确认已执行 python manage.py seed_demo，账号为 demo_member / member123456"
    )
    location = posted.headers.get("Location", "")
    assert location == "/" or location.endswith("/"), f"登录后应回首页，实际 Location={location}"
    assert "sessionid" in session.cookies, "登录成功后应有 sessionid Cookie"
    center = session.get(f"{base_url}/member/", timeout=8, allow_redirects=False)
    assert center.status_code == 200, f"登录态无效，访问会员中心得到 {center.status_code}"
    return session


@pytest.fixture
def sample_product(anon_session, base_url):
    page = anon_session.get(f"{base_url}/shop/", timeout=8)
    assert page.status_code == 200, f"花市打不开：{page.status_code}"
    match = _PRODUCT_HREF.search(page.text)
    assert match, "花市页没有商品详情链接，请先 python manage.py seed_demo"
    pk = int(match.group(1))
    detail = anon_session.get(f"{base_url}/shop/{pk}/", timeout=8)
    assert detail.status_code == 200
    name_match = re.search(r"<h1>([^<]+)</h1>", detail.text)
    name = name_match.group(1).strip() if name_match else ""
    assert name, "详情页没有商品名"
    return {"id": pk, "name": name}
