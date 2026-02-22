+++
title = "Province Open API"
template = "index.html"
+++

## Ví dụ với [HTTPie](https://httpie.io)

#### Liệt kê:

```sh
http -v https://provinces.open-api.vn/api/v1/ depth==2
```

Request:

```http
GET /api/v1/?depth=2 HTTP/1.1
Host: provinces.open-api.vn
```

Response:

```http
HTTP/1.1 200 OK
Connection: keep-alive
Content-Type: application/json
Transfer-Encoding: chunked

[
  {
    "name": "Thành phố Hà Nội",
    "code": 1,
    "division_type": "thành phố trung ương",
    "phone_code": 24,
    "codename": "thanh_pho_ha_noi",
    "districts": [
      {
        "name": "Quận Ba Đình",
        "code": 1,
        "codename": "quan_ba_dinh",
        "division_type": "quận",
        "province_code": 1,
        "wards": null
      },
      {
        "name": "Quận Hoàn Kiếm",
        "code": 2,
        "codename": "quan_hoan_kiem",
        "division_type": "quận",
        "province_code": 1,
        "wards": null
      },
      ...
    ]
  },
  ...
]
```

#### Tìm kiếm:

```sh
http -v https://provinces.open-api.vn/api/v1/d/search/ q==Y
```

Request:

```http
GET /api/v1/d/search/?q=Y HTTP/1.1
Host: provinces.open-api.vn
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
content-length: 71

[
    {
        "name": "Huyện Ý Yên",
        "code": 360,
        "matches": {
            "y": [6, 7]
        },
        "score": 6
    }
]
```

## Ví dụ với [Nushell](https://www.nushell.sh)

```nu
❯ http get https://provinces.open-api.vn/api/v2/w/from-legacy/?({ legacy_name: 'Tóc Tiên' } | url build-query)
╭───┬─────────────┬─────────────────────────────────╮
│ # │ source_code │              ward               │
├───┼─────────────┼─────────────────────────────────┤
│ 0 │       26731 │ ╭───────────────┬─────────────╮ │
│   │             │ │ name          │ Xã Châu Pha │ │
│   │             │ │ code          │ 26728       │ │
│   │             │ │ division_type │ xã          │ │
│   │             │ │ codename      │ xa_chau_pha │ │
│   │             │ │ province_code │ 79          │ │
│   │             │ ╰───────────────┴─────────────╯ │
╰───┴─────────────┴─────────────────────────────────╯
❯ http get https://provinces.open-api.vn/api/v2/w/26728/to-legacies/
╭──────┬───────────────┬─────────┬─────────────────┬───────────────┬─────────────────┬─────────────────╮
│    # │     name      │  code   │  division_type  │   codename    │  district_code  │  province_code  │
├──────┼───────────────┼─────────┼─────────────────┼───────────────┼─────────────────┼─────────────────┤
│    0 │ Xã Châu Pha   │   26728 │ xã              │ xa_chau_pha   │             754 │              77 │
│    1 │ Xã Tóc Tiên   │   26731 │ xã              │ xa_toc_tien   │             754 │              77 │
╰──────┴───────────────┴─────────┴─────────────────┴───────────────┴─────────────────┴─────────────────╯
```
