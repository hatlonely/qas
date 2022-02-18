该目录是 grpc driver 测试目录，文件来自 grpc 官网 <https://grpc.io/docs/languages/python/basics/>

- `route_guide.proto`：协议文件
- `server.py`: 服务实现，用来测试 grpc driver

## 测试服务流程

1. 代码生成（此处代码生成是给 `server.py` 用的，`qas` 会自动生成代码，执行仅依赖 proto 文件）

```shell
cd ops/grpc && python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. route_guide.proto
```

2. 启动服务

```shell
cd ops/grpc && python3 server.py
```

3. 执行测试

```shell
qas -t ops/example-docs/driver/grpc
```
