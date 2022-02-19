## thrift

### 启动参数

- `proto`: `string`，协议文件路径，必填
- `endpoint`: `string`，服务地址，`host:port`，必填
- `service`: `string`，服务名，必填

```yaml
ctx:
  rpc:
    type: thrift
    args:
      proto: ops/thrift/tutorial.thrift
      endpoint: localhost:9090
      service: Calculator
```

### 发起请求

**请求**

- `method`: `string`，请求方法
- `args`: `[any]`, 参数列表
    - `type`: `string`，参数类型
    - `args`: `[string, any]`构造参数

```json
{
  "method": "calculate",
  "args": [
    1234,
    {
      "args": {
        "num1": 4,
        "num2": 8,
        "op": 3
      },
      "type": "Work"
    }
  ]
}
```

**返回**

```json
32
```
