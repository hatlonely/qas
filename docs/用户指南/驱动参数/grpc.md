## GRPC

### 启动参数

- `proto`: `string`，协议文件路径，必填
- `endpoint`: `string`，服务地址，`host:port`，必填
- `service`: `string`，服务名，必填
- `include`: `[string]`，proto 协议包含目录，可选参数

```yaml
ctx:
  rpc:
    type: grpc
    args:
      proto: ops/grpc/route_guide.proto
      endpoint: localhost:50051
      service: RouteGuide
      include:
```

### 发起请求

**请求**

- `method`: `string`，请求方法
- `type`: `string`，参数类型
- `args`: `[string, any]`，构造参数

```json
{
  "method": "GetFeature",
  "type": "Point",
  "args": {
    "latitude": 409146138,
    "longitude": 746188906
  }
}
```

**返回**

```json
{
  "location": {
    "latitude": 409146138,
    "longitude": 746188906
  }
}
```
