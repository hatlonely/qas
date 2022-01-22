## mysql

mysql client

### 启动参数

- `host`: `string`，主机地址，默认 localhost
- `port`: `int`，主机端口，默认 3306
- `username`: `string`，用户名，必填
- `password`: `string`，密码，必填
- `database`: `string`，数据库名，必填

```yaml
ctx:
  db:
    type: mysql
    args:
      host: "localhost"
      port: 3306
      username: "hatlonely"
      password: "keaiduo1"
      database: "hatlonely"
```

### 执行 sql

**请求**

- `cmd`: `string`，执行 sql 后调用命令，默认 `sql`，可选值 `sql/fetchone/fetchall`
    - `sql`: 仅执行 sql
    - `fetchone`: 执行 sql 后获取一条结果
    - `fetchall`: 执行 sql 后获取所有结果
- `sql`: `string`，sql，支持 `%s` 表示位置参数，必填
- `args`: `[string]`，sql 中的位置参数，默认为空

**返回**

- `code`: `string`，执行结果，成功返回 `OK`
    - `OK`: 成功
    - `OperationalError`: 操作类错误
- `res`: `[string, any]`，查询结果
- `err`: `[string, any]`，错误结果
    - `type`: `string`，错误类型，目前仅有一种 `OperationalError`
    - `args`: `[string]`，错误返回结果

```yaml
case:
  - name: MysqlExample
    step:
      - ctx: db
        req:
          sql: |
            INSERT INTO `users` (`email`, `password`) VALUES (%s, %s), (%s, %s)
          args:
            - "hatlonely@foxmail.com"
            - "123456"
            - "playjokes@foxmail.com"
            - "456789"
        res:
          code: OK
      - ctx: db
        req:
          cmd: fetchone
          sql: |
            SELECT `id`, `password` FROM `users` WHERE `email`=%s
          args:
            - "hatlonely@foxmail.com"
        res:
          code: OK
          res:
            password: "123456"
      - ctx: db
        req:
          cmd: fetchall
          sql: |
            SELECT * FROM `users` WHERE 1=1
        res:
          code: OK
          res: [{
            "id": 1,
            "email": "hatlonely@foxmail.com",
            "password": "123456"
          }, {
            "id": 2,
            "email": "playjokes@foxmail.com",
            "password": "456789"
          }]
      - ctx: db
        req:
          cmd: fetchone
          sql: |
            SELECT `id`, `invalidField` FROM `users` WHERE `email`=%s
          args:
            - "hatlonely@foxmail.com"
        res:
          code: OperationalError
          err:
            type: OperationalError
            args:
              - 1054
              - "Unknown column 'invalidField' in 'field list'"
```
