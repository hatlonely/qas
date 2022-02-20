## sls

### 启动参数

- `Endpoint`: `string`，服务地址，必填
- `AccessKeyId`: `string`，阿里云访问凭证 id，必填
- `AccessKeySecret`: `string`，阿里云访问凭证 secret，必填

```yaml
ctx:
  sls:
    type: sls
    args:
      AccessKeyId: xxx
      AccessKeySecret: xxx
      Endpoint: cn-shanghai.log.aliyuncs.com
```

### 发起请求

#### PutLogs

**请求**

- `Action`: `string`，服务方法，`PutLogs`
- `Project`: `string`，项目，必填
- `Logstore`: `string`，日志桶，必填
- `Topic`: `string`，主题，默认为空
- `Source`: `string`，文件名，默认为空
- `HashKey`: `string`，哈希值，默认为空
- `LogTags`: `[string, string]`，日志 tag
- `LogItems`: `[LogItem]`，日志条目
    - `Timestamp`: `int`，时间戳
    - `Contents`: `[string, string]`，日志内容，`key/value` 格式

**返回**

```json
{
  "RequestId": "6211D94B7F383EC3BB07B305",
  "Header": {
    "Server": "Tengine",
    "Content-Length": "0",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "*",
    "Date": "Sun, 20 Feb 2022 06:01:47 GMT",
    "x-log-append-meta": "true",
    "x-log-time": "1645336907",
    "x-log-requestid": "6211D94B7F383EC3BB07B305"
  },
  "Body": ""
}
```

#### GetLogs

**请求**

- `Action`: `string`，服务方法，`GetLogs`
- `Project`: `string`，项目，必填
- `Logstore`: `string`，日志桶，必填
- `FromTime`: `int`，开始时间戳
- `ToTime`: `int`，结束时间戳
- `Topic`: `string`，主题，默认为空
- `Query`: `string`，查询 sql，默认为空
- `Offset`: `int`，偏移量，默认为 0
- `Size`: `int`，最多返回日志数，默认为 100
- `Reverse`: `bool`，逆序，默认 `false`
- `PowerSQL`: `bool`，默认 `false`

**返回**

```json
{
  "RequestId": "6211D94B0BD61890F75C75B8",
  "Header": {
    "Server": "Tengine",
    "Content-Type": "application/json",
    "Content-Length": "1709",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "*",
    "Date": "Sun, 20 Feb 2022 06:01:47 GMT",
    "x-log-agg-query": "",
    "x-log-elapsed-millisecond": "2",
    "x-log-has-sql": "false",
    "x-log-processed-rows": "7",
    "x-log-query-info": "{\"keys\":[\"key1\",\"key2\",\"key3\",\"__topic__\",\"__source__\",\"__tag__:tag1\",\"__tag__:tag2\",\"__tag__:__client_ip__\",\"__tag__:__receive_time__\"],\"terms\":[[\"*\",\"\"]]}",
    "x-log-time": "1645336907",
    "x-log-where-query": "",
    "x-log-count": "7",
    "x-log-progress": "Complete",
    "x-log-requestid": "6211D94B0BD61890F75C75B8",
    "x-tlm-type": "logging"
  },
  "Body": [
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336523",
      "__time__": "1645336523"
    },
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336530",
      "__time__": "1645336529"
    },
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336575",
      "__time__": "1645336575"
    },
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336597",
      "__time__": "1645336596"
    },
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336605",
      "__time__": "1645336605"
    },
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336693",
      "__time__": "1645336693"
    },
    {
      "key1": "val1",
      "key2": "val2",
      "key3": "val3",
      "__topic__": "test-topic",
      "__source__": "test-source",
      "__tag__:tag1": "val1",
      "__tag__:tag2": "val2",
      "__tag__:__client_ip__": "123.123.43.36",
      "__tag__:__receive_time__": "1645336876",
      "__time__": "1645336876"
    }
  ]
}
```
