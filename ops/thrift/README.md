该目录是 thrift driver 测试目录，文件来着 thrift 官网 <https://thrift.apache.org/tutorial/py.html>

- `shared.thrift`：共享结构协议文件
- `tutorial.thrift`: 服务协议文件
- `server.py`: 服务实现，用来测试 thrift driver

## 测试服务流程

1. 代码生成（此处代码生成是给 `server.py` 用的，`qas` 会自动生成代码，执行仅依赖 thrift 文件）

```shell
cd ops/thrift && thrift -r --gen py tutorial.thrift
```

2. 启动服务

```shell
cd ops/thrift && python3 server.py
```

3. 执行测试

```shell
qas -t ops/example-docs/driver/thrift
```
