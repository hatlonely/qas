## mongo

### 启动参数

### 发起请求

#### insertOne

**请求**

- `cmd`: `string`，常量 `insertOne`
- `collection`: `string`，集合，必填
- `document`: `[string, any]`，文档

**返回**

```yaml
{
  "_id": "61f0fb17d41f2ac96c700eac"
}
```

```yaml
ctx: mongo
req:
  cmd: insertOne
  collection: "test_collection"
  document: {
    "key1": "value1",
    "key2": "value2",
    "key3": {
      "key4": "value4",
      "key5": 5,
      "key6": [
          "value61",
          "value62"
      ],
      "key7": [{
        "key8": "value8"
      }]
    }
  }
res:
  "#_id": "len(val) != 0"
```

#### updateOne

**请求**

- `cmd`: `string`，常量 `updateOne`
- `collection`: `string`，集合，必填
- `_id`: `string`，object id，用于过滤
- `filter`: `[string, any]`，过滤规则
- `update`: `[string, any]`，更新值
- `upsert`: `bool`，不存在时直接插入，默认为 `false`

**返回**

```json
{
  "acknowledged": true,
  "matchedCount": 1,
  "modifiedCount": 1
}
```

```yaml
ctx: mongo
req:
  cmd: updateOne
  collection: "test_collection"
  "#_id": "case.steps[0].res['_id']"
  update: {
    "key3": {
      "key4": "newval4"
    }
  }
res:  {
  "acknowledged": true,
  "matchedCount": 1,
  "modifiedCount": 1
}
```

#### deleteOne

**请求**

- `cmd`: `string`，常量 `deleteOne`
- `collection`: `string`，集合，必填
- `_id`: `string`，object id，用于过滤
- `filter`: `[string, any]`，过滤规则

**返回**

```json
{
  "acknowledged": true,
  "deleteCount": 1
}
```

```yaml
ctx: mongo
req:
  cmd: deleteOne
  collection: "test_collection"
  "#_id": "case.steps[0].res['_id']"
res: {
  "acknowledged": true,
  "deleteCount": 1
}
```

#### findOne

**请求**

- `cmd`: `string`，常量 `findOne`
- `collection`: `string`，集合，必填
- `_id`: `string`，object id，用于过滤
- `filter`: `[string, any]`，过滤规则

**返回**

```json
{
  "_id": "61f0fb63f7a7b914c4aa2620",
  "key1": "value1",
  "key2": "value2",
  "key3": {
    "key4": "newval4",
    "key5": 5,
    "key6": [
      "value61",
      "value62"
    ],
    "key7": [
      {
        "key8": "value8"
      }
    ]
  }
}
```

```yaml
ctx: mongo
req:
  cmd: findOne
  collection: "test_collection"
  "#_id": "case.steps[0].res['_id']"
res: {
  "key1": "value1",
  "key2": "value2",
  "key3": {
    "key4": "newval4",
    "key5": 5,
    "key6": [
        "value61",
        "value62"
    ],
    "key7": [ {
      "key8": "value8"
    } ]
  }
}
```

### 链接

- [完整代码](/ops/example-docs/driver/mongo/ctx.yaml)
