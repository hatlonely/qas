## ots

### 启动参数

- `Endpoint`: `string`，服务地址，必填
- `AccessKeyId`: `string`，阿里云访问凭证 id，必填
- `AccessKeySecret`: `string`，阿里云访问凭证 secret，必填
- `Instance`: `string`，实例名

```yaml
ctx:
  ots:
    type: ots
    args:
      AccessKeyId: ${OTS_AK}
      AccessKeySecret: ${OTS_SK}
      Endpoint: ${OTS_ENDPOINT}
      Instance: ${OTS_INSTANCE}
```

### 发起请求

#### ListTable

**请求**

- `Action`: `string`，服务方法，常量 `ListTable`

**返回**

- Table 数组

#### CreateTable

**请求**

- `Action`: `string`，服务方法，常量 `CreateTable`
- `TableMeta`: 表元信息
    - `TableName`: `string`，表名，必填
    - `SchemaEntry`: `[object]`，主键列
        - `Name`: `string`，名字
        - `Type`: `string`，类型，取值 `STRING / INTEGER / BOOLEAN / DOUBLE / BINARY`
    - `DefinedColumns`: `[object]`，预定义列
        - `Name`: `string`，名字
        - `Type`: `string`，类型，取值 `STRING / INTEGER / BOOLEAN / DOUBLE / BINARY`
- `TableOptions`: 表选项
    - `TimeToLive`: `int`，自动过期时间 ttl，默认 -1，永不过期
    - `MaxVersion`: `int`，最大版本数量，默认 1
    - `MaxTimeDeviation`: `int`，数据有效版本偏差，默认 86400

**返回**

空

#### DeleteTable

**请求**

- `Action`: `string`，服务方法，常量 `DeleteTable`
- `TableName`: `string`，表名，必填

**返回**

空

#### PutRow

**请求**

- `Action`: `string`，服务方法，常量 `PutRow`
- `TableName`: `string`，表名，必填
- `Row`: `object` 行
    - `PrimaryKey`: `[object]`，主键
        - `Key`: `string`，主键名
        - `Val`: `any`，值
    - `AttributeColumns`: `[string, any]`，列
- `Condition`: `string`，条件，默认 `IGNORE`，取值 `IGNORE / EXPECT_EXIST / EXPECT_NOT_EXIST`

**返回**

空

#### GetRow

**请求**

- `Action`: `string`，服务方法，常量 `GetRow`
- `TableName`: `string`，表名，必填
- `PrimaryKey`: `[object]`，主键
    - `Key`: `string`，主键名
    - `Val`: `any`，值
- `MaxVersion`: `int`，最大版本，默认 1

**返回**

`[string, any]`，列

#### DeleteRow

**请求**

- `Action`: `string`，服务方法，常量 `DeleteRow`
- `TableName`: `string`，表名，必填
- `PrimaryKey`: `[object]`，主键
    - `Key`: `string`，主键名
    - `Val`: `any`，值
- `Condition`: `string`，条件，默认 `IGNORE`，取值 `IGNORE / EXPECT_EXIST / EXPECT_NOT_EXIST`

**返回**

空

#### GetRange

**请求**

"TableName": REQUIRED,
            "Direction": "FORWARD",
            "StartPrimaryKey": [{
                "Key": REQUIRED,
                "Val": tablestore.INF_MIN
            }],
            "EndPrimaryKey": [{
                "Key": REQUIRED,
                "Val": tablestore.INF_MAX,
            }]

- `Action`: `string`，服务方法，常量 `GetRange`
- `TableName`: `string`，表名，必填
- `Direction`: `string`，遍历方向，默认 `FORWARD`，取值 `FORWARD / BACKWARD`
- `StartPrimaryKey`: `[object]`，主键
    - `Key`: `string`，主键名
    - `Val`: `any`，值，默认 tablestore.INF_MIN
- `EndPrimaryKey`: `[object]`，主键
    - `Key`: `string`，主键名
    - `Val`: `any`，值，默认 tablestore.INF_MAX
- `MaxVersion`: `int`，最大版本，默认 1

**返回**

`[[string, any]]`，列数组

```yaml
setUp:
  - name: CreateTable
    step:
      - ctx: ots
        req:
          Action: CreateTable
          TableMeta:
            TableName: TestQAS
            SchemaEntry:
              - Name: PK1
                Type: STRING
              - Name: PK2
                Type: STRING
            TableOptions:
              TimeToLive: -1
              MaxVersion: 1
              MaxTimeDeviation: 86400

tearDown:
  - name: DeleteTable
    step:
      - ctx: ots
        req:
          Action: DeleteTable
          TableName: TestQAS

case:
  - name: OTSExample
    desc: |
      参考: api 文档 <https://help.aliyun.com/document_detail/27303.html>
    step:
      - ctx: ots
        req:
          Action: ListTable
        res:
      - ctx: ots
        req:
          Action: PutRow
          TableName: TestQAS
          Row:
            PrimaryKey:
              - Key: PK1
                Val: pkVal1
              - Key: PK2
                Val: pkVal2
            AttributeColumns:
              key1: val1
              key2: val2
      - ctx: ots
        req:
          Action: GetRow
          TableName: TestQAS
          PrimaryKey:
            - Key: PK1
              Val: pkVal1
            - Key: PK2
              Val: pkVal2
        res:
          key1: val1
          key2: val2
      - ctx: ots
        req:
          Action: GetRange
          TableName: TestQAS
          StartPrimaryKey:
            - Key: PK1
            - Key: PK2
          EndPrimaryKey:
            - Key: PK1
            - Key: PK2
        res:
          - PK1: pkVal1
            PK2: pkVal2
            key1: val1
            key2: val2
      - ctx: ots
        req:
          Action: DeleteRow
          TableName: TestQAS
          PrimaryKey:
            - Key: PK1
              Val: pkVal1
            - Key: PK2
              Val: pkVal2
```