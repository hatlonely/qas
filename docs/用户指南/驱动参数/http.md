## http

http client

### 启动参数

- `endpoint`: `string`，url 地址，必填，例如：`http://echo.jsontest.com/`

```yaml
ctx:
  jsontest:
    type: http
    args:
      endpoint: http://echo.jsontest.com
```

### 发起请求

**请求**

- `endpoint`: `string`，url 地址，默认使用启动参数中的 endpoint
- `path`: `string`，url path，默认为空
- `method`: `string`，http 方法，默认 POST
- `headers`: `[string, string]`，请求头部，默认为空
- `params`: `[string, string]`，query 参数，默认为空
- `data`: `string`，请求 body，默认为空
- `json`: `any`，json body，默认为空
- `timeout`: `string`，超时时间，默认 1s
- `allowRedirects`: `bool`，是否允许重定向，默认为 true


**返回**

- `status`: `int`，返回 http 状态码
- `headers`: `[string, string]`，返回头部
- `text`: `string`，返回 body
- `json`: `any`，按 json 格式解析 body

```yaml
case:
  - name: HttpExample
    step:
      - ctx: jsontest
        req:
          path: /key/value/one/two
          timeout: 10s
        res:
          status: 200
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
            "#X-Cloud-Trace-Context": "len(val) == 32"
          }
          json: {
            "one": "two",
            "key": "value"
          }
```
