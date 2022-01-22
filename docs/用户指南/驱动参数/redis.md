## redis

redis 客户端

### 启动参数

- `host`: `string`，服务地址，默认 localhost
- `port`: `int`，服务端口，默认 6379
- `db`: `int`，数据库，默认 0
- `password`: `string`，密码，默认为空

```yaml
ctx:
  redis:
    type: redis
    args:
      host: "localhost"
      port: 6379
      db: 0
      password:
```

### 执行命令

#### set

**请求**

- `cmd`: `string`，命令，常量 `set`
- `key`: `string`，key，键，必填
- `val`: `string`，val，值，必填

**返回**

- `ok`: `bool`，是否成功

#### setJson

**请求**

- `cmd`: `string`，命令，常量 `set`
- `key`: `string`，key，键，必填
- `val`: `any`，val，值，在 redis 中以 json 编码写入，必填

**返回**

- `ok`: `bool`，是否成功

#### get

**请求**

- `cmd`: `string`，命令，常量 `get`
- `key`: `string`，key，键，必填

**返回**

- `val`: `string`，val，值

#### getJson

**请求**

**请求**

- `cmd`: `string`，命令，常量 `get`
- `key`: `string`，key，键，必填

**返回**

- `val`: `string`，值，以 json 解码字符串

#### del

**请求**

- `cmd`: `string`，命令，常量 `del`
- `key`: `string`，key，键，必填

**返回**

- `ok`: `bool`，是否成功


#### hset

**请求**

- `cmd`: `string`，命令，常量 `set`
- `key`: `string`，key，键，必填
- `field`: `string`，field，域，必填
- `val`: `string`，val，值，必填

**返回**

- `n`: `int`，field 修改数

#### hget

**请求**

- `cmd`: `string`，命令，常量 `set`
- `key`: `string`，key，键，必填
- `field`: `string`，field，域，必填

**返回**

- `val`: `string`，val，值

#### hdel

**请求**

- `cmd`: `string`，命令，常量 `set`
- `key`: `string`，key，键，必填
- `field`: `string`，field，域，必填

**返回**

- `n`: `int`，field 修改数

```yaml
case:
  - name: RedisExample
    step:
      - ctx: redis
        req:
          cmd: set
          key: name
          val: hatlonely
          exp: 60
        res:
          ok: true
      - ctx: redis
        req:
          cmd: get
          key: name
        res:
          val: hatlonely
      - ctx: redis
        req:
          cmd: setJson
          key: obj
          val:
            key1: val1
            key2: val2
        res:
          ok: true
      - ctx: redis
        req:
          cmd: getJson
          key: obj
        res:
          key1: val1
          key2: val2
      - ctx: redis
        req:
          cmd: hset
          key: hname
          field: key
          val: val
        res:
          n: 1
      - ctx: redis
        req:
          cmd: hget
          key: hname
          field: key
        res:
          val: val
```
