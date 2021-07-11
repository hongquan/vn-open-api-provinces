+++
title = "Province Open API"
template = "index.html"
+++

Ví dụ với [HTTPie](https://httpie.io/):

```sh
http -v https://provinces.open-api.vn/api/ depth==2
```

Request:

```http
GET /api/?depth=2 HTTP/1.1
Host: provinces.open-api.vn
```

Response:

```http
HTTP/1.1 200 OK
Content-Encoding: gzip
Content-Type: application/json

[
  {
    "code": 1,
    "codename": "thanh_pho_ha_noi",
    "districts": [
      {
        "code": 1,
        "codename": "quan_ba_dinh",
        "division_type": "quận",
        "name": "Quận Ba Đình",
        "province_code": 1,
        "wards": null
      },
      {
        "code": 2,
        "codename": "quan_hoan_kiem",
        "division_type": "quận",
        "name": "Quận Hoàn Kiếm",
        "province_code": 1,
        "wards": null
      },
      ...
    ]
  },
  ...
]
```
