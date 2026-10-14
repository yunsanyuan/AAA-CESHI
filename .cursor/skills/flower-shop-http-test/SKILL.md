---
name: flower-shop-http-test
description: Writes and extends 花间集 HTTP black-box tests using pytest and requests (Session + CSRF, no REST/JWT). Use when adding interface tests, pytest+requests cases, login/cart/member HTTP checks, or when the user mentions 接口测试, CSRF, session cookie, or live runserver tests.
---

# 花间集 HTTP 接口测试

本仓库是测试仓。被测系统是独立仓库 [yunsanyuan/sanyuan](https://github.com/yunsanyuan/sanyuan)，不要在本仓库生成 Django 业务代码。

## 禁止编造的接口

不要生成：

- `/api/`、DRF、JSON body 断言
- `Authorization: Bearer`、JWT
- 把 Admin 商品 CRUD 当会员端接口

先读 [reference.md](reference.md) 里的真实入口表，再写用例。

## 工作流

1. 把场景收成「方法 + 路径 + 成功长什么样」，对照 `tests/`：已有则补边界，没有再新增 `test_*.py`。
2. 登录与 POST 一律走 `conftest.py` 的 `extract_csrf` + `member_session` / `anon_session`。
3. 断言只用 `status_code`、`Location`、Cookie、HTML 关键字。
4. **不要**自动化结算支付、充值入账、后台退款。加购可以，只断言购物车里出现商品名。
5. 会员账号用 `demo_member` / `member123456`。不要用 `admin` / `staff` 测前台。
6. 在本仓库根目录跑 `pytest`。被测站点必须已 `runserver`。

## POST 合同

```
GET 表单页 → extract_csrf(html) → POST csrfmiddlewaretoken + 字段
headers.Referer = 表单页 URL
allow_redirects=False
```

缺 CSRF 的 POST 期望 **403**。未登录访问 `/member/` 期望 **302** 且 Location 含 `/accounts/login/`。

## 改代码边界

- 可以改：本仓库 `tests/`、`conftest.py`、本 skill、README
- 不要为了「好测」去改 sanyuan 的视图变成 REST
