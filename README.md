# 花间集 · HTTP 接口自动化

用 `pytest` + `requests` 对正在运行的花店会员系统做黑盒 HTTP 测试。

被测系统（业务代码不在本仓库）：

**[yunsanyuan/sanyuan](https://github.com/yunsanyuan/sanyuan)** · Django 5.2 模板站点「花间集」

本仓库只含测试：对着 `http://127.0.0.1:8000` 发真实 HTTP，断言状态码、重定向、Cookie 和 HTML 关键字。站点返回 HTML，登录靠 Session Cookie，没有 `/api/`，没有 JWT。

| 场景 | 入口 | 期望 |
| --- | --- | --- |
| 登录 | `POST /accounts/login/` | 302，Location `/`，Cookie 有 `sessionid` |
| 商品 | `GET /shop/`、`GET /shop/<id>/` | 200，含「花市」或商品名 |
| 加购 | `POST /shop/<id>/add/` 再 `GET /orders/cart/` | 302 后购物车页出现该花 |
| 会员 | `GET /member/`、`GET /member/profile/` | 登录后 200 |
| 异常 | 未知商品、未登录、缺密码、假 `sessionid`、缺 CSRF | 404 / 302 / 仍停在登录页 / 403 |

默认不加结算、不模拟支付，避免往演示库写订单。设计说明见 [docs/设计说明.md](docs/设计说明.md)。

---

## 怎么用 Cursor 写出来的

先读被测仓库的 URL 和登录方式，把架构约束写进对话，再生成用例，最后对照真实响应改断言。

发给 Cursor 的约束：

- 不要生成 `/api/`、JSON、Bearer token
- 只打现有路径：登录、花市/详情、加购、会员中心/资料
- `conftest.py` 提供 `member_session`：GET 登录页 → CSRF → POST → 检查 302 和 `sessionid`
- 断言 `status_code`、`Location`、Cookie、HTML；异常覆盖 404、未登录 302、缺 password
- 不要改被测系统源码，不要跑结算

生成后人工核对：

- 登录成功是 **302 + Location `/`**，不是 200 JSON
- POST 必须带 **csrfmiddlewaretoken**
- 用 `demo_member`，不用 `admin`（员工会进 `/admin/`）
- 加购只断言购物车里出现商品名，不断言数量一定是 1
- 「非法凭证」写成假 `sessionid` Cookie

续写用例时使用本仓库 Skill：`.cursor/skills/flower-shop-http-test/`。

本地对运行中的花间集跑通 11 条。

---

## 怎么跑

需要 **Python 3.12+**、两个终端：被测系统先起来，再跑本仓库。

### 1. 启动花间集

```bash
git clone https://github.com/yunsanyuan/sanyuan.git
cd sanyuan
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # macOS / Linux: cp .env.example .env
```

在 `.env` 填写 MySQL 密码，并建库 `flower_member`（utf8mb4）。然后：

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

浏览器打开 http://127.0.0.1:8000 能进首页即可。演示会员：`demo_member` / `member123456`。

更完整的部署步骤以 [sanyuan README](https://github.com/yunsanyuan/sanyuan) 为准。

### 2. 跑本仓库

另开终端，在**本仓库根目录**（不要套进 sanyuan 里）：

```bash
python -m pip install -r requirements.txt
copy .env.example .env          # macOS / Linux: cp .env.example .env
pytest
```

`.env` 可改 `BASE_URL`。默认账号与 `seed_demo` 一致。

连不上服务器时，fixture 会退出并提示先启动花间集，不是用例写错。

GitHub Actions 对本仓库做 `pytest --collect-only`（CI 不启演示站）。真正打 HTTP 仍要本机 `runserver`。

---

## 目录

```
conftest.py                 探活、CSRF、登录 session、抽样商品
tests/test_login.py         登录成功 / 缺密码
tests/test_shop.py          花市、详情
tests/test_cart.py          加购后看购物车
tests/test_member.py        会员中心、资料
tests/test_errors.py        404、未登录、假 session、缺 CSRF
docs/设计说明.md            为什么不是 REST、分层、边界
.cursor/skills/...          给 Cursor 续写用例的约束
.github/workflows/ci.yml    collect-only
```

`member_session`：GET 登录页 → 解析 CSRF → POST 用户名密码 → 302 + `sessionid` → GET `/member/` 为 200。加购、资料页复用这次登录。
