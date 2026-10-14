# 花间集真实 HTTP 入口

被测系统：[yunsanyuan/sanyuan](https://github.com/yunsanyuan/sanyuan)。断言针对 HTML，不是 JSON。

## 本仓库覆盖的入口

| 场景 | 方法 | 路径 | 成功 | 不要做 |
| --- | --- | --- | --- | --- |
| 登录 | POST | `/accounts/login/` | 302，Location `/`，Cookie `sessionid` | 不要用 admin 账号 |
| 登录缺参 | POST | `/accounts/login/` 无 password | 200，仍在登录页「欢迎回来」 | 不要期望 401 JSON |
| 花市 | GET | `/shop/` | 200，含「花市」 | |
| 详情 | GET | `/shop/<id>/` | 200，含商品名；「加入购物车」或「售罄」 | id 从列表页 `href` 刮，不要写死 1 |
| 加购 | POST | `/shop/<id>/add/` | 302 到 `/orders/cart/` | 必须 CSRF；不断言数量==1 |
| 购物车 | GET | `/orders/cart/` | 200，含「购物车」和商品名 | |
| 会员中心 | GET | `/member/` | 登录 200；匿名 302 登录 | |
| 资料 | GET | `/member/profile/` | 200，含「会员资料」和用户名 | |
| 未知商品 | GET | `/shop/999999/` | 404 | |
| 假会话 | GET | `/member/` + 假 `sessionid` | 302 登录 | 不是 Bearer |
| 缺 CSRF 加购 | POST | `/shop/<id>/add/` 无 token | 403 | Session 可以已登录 |

## 默认不要自动化

| 路径 | 原因 |
| --- | --- |
| `POST /orders/checkout/` | 真实下单 |
| `POST /orders/<id>/pay/` | 模拟支付入账 |
| `POST /member/recharge/`、`.../pay/` | 储值入账 |
| `POST /member/coupons/<id>/claim/` | 领券占名额 |
| `/admin/`、`/dashboard/` | 不是会员接口层 |

## Fixture（`conftest.py`）

- `base_url`：默认 `http://127.0.0.1:8000`
- `anon_session`：新 `requests.Session()`
- `member_session`：GET 登录 → CSRF POST → 302 `/` → GET `/member/` 200
- `sample_product`：从 `/shop/` 解析第一个 `/shop/<id>/`，再读详情 `<h1>`
- `extract_csrf`：两种 hidden input 属性顺序都要匹配

## 跑法

被测系统 `runserver` 之后，在本仓库根目录：

```bash
pytest
```

CI 只 `--collect-only`。
