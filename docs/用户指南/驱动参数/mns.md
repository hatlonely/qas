## mns

### 启动参数

- `Endpoint`: `string`，服务地址，必填
- `AccessKeyId`: `string`，阿里云访问凭证 id，必填
- `AccessKeySecret`: `string`，阿里云访问凭证 secret，必填

```yaml
ctx:
  mns:
    type: mns
    args:
      AccessKeyId: ${MNS_AK}
      AccessKeySecret: ${MNS_SK}
      Endpoint: ${MNS_ENDPOINT}
```

### 发起请求

#### PublishMessage

**请求**

- `Action`: `string`，服务方法，常量 `PublishMessage`
- `Topic`: `string`，主题，必填
- `MessageBody`: `string`，消息
- `Body`: `string`，以 json 格式写入 MessageBody，仅当 MessageBody 为空时生效
- `MessageTag`: `string`，消息标签
- `DirectMail`: `string`，邮箱
- `DirectSms`: `string`，短信

**返回**

```json
{
  "Status": 201,
  "Header": {
    "Server": "AliyunMQS",
    "Date": "Sat, 22 Jan 2022 15:20:12 GMT",
    "Content-Type": "text/xml;charset=utf-8",
    "Content-Length": "208",
    "Connection": "keep-alive",
    "x-mns-version": "2015-06-06",
    "x-mns-request-id": "61EC20AC324430C923273326"
  },
  "RequestId": "61EC20AC324430C923273326",
  "MessageId": "7F3D61FE01E545217FCC712779C9BBF5",
  "MessageBodyMD5": "5EB63BBBE01EEED093CB22BB8F5ACDC3"
}
```

#### ReceiveMessage

**请求**

- `Action`: `string`，服务方法，常量 `ReceiveMessage`
- `Queue`: `string`，队列，必填
- `WaitSeconds`: `int`，等待时间，默认 -1，一直等待
- `AutoRelease`: `bool`，自动释放，默认 `true`
- `Base64Decode`: `bool`，自动 base64 解码 body，默认 `false`

**返回**

```json
{
  "Status": 200,
  "Header": {
    "Server": "AliyunMQS",
    "Date": "Sat, 22 Jan 2022 15:26:12 GMT",
    "Content-Type": "text/xml;charset=utf-8",
    "Content-Length": "852",
    "Connection": "keep-alive",
    "x-mns-version": "2015-06-06",
    "x-mns-request-id": "61EC22133132375E238EDB6E"
  },
  "RequestId": "61EC22133132375E238EDB6E",
  "MessageId": "772F147D01E504307FCF712CF461D5D2",
  "ReceiptHandle": "8-BzvT93jFnzuz6zcJz0zhAzcUxr0B2GnZl",
  "MessageBodyMD5": "73034DE019DE7AEBCB55FD466F5316B0",
  "MessageBody": "{\"TopicOwner\":\"1023210024677934\",\"Message\":\"{\\\"key1\\\": \\\"val1\\\", \\\"key2\\\": \\\"val2\\\"}\",\"Subscriber\":\"1023210024677934\",\"PublishTime\":\"1642865171548\",\"SubscriptionName\":\"imm-test-hl-mns-queue-shanghai\",\"MessageMD5\":\"775A9B1CEDDB5F8978836DB24DF90A01\",\"TopicName\":\"imm-test-hl-mns-topic-shanghai\",\"MessageId\":\"7F3D61FE01E5656C7F9D712CF45CA356\"}",
  "EnqueueTime": 1642865171557,
  "NextVisibleTime": 1642865202119,
  "FirstDequeueTime": 1642865172119,
  "DequeueCount": 1,
  "Priority": 8,
  "Body": {
    "TopicOwner": "1023210024677934",
    "Message": "{\"key1\": \"val1\", \"key2\": \"val2\"}",
    "Subscriber": "1023210024677934",
    "PublishTime": "1642865171548",
    "SubscriptionName": "imm-test-hl-mns-queue-shanghai",
    "MessageMD5": "775A9B1CEDDB5F8978836DB24DF90A01",
    "TopicName": "imm-test-hl-mns-topic-shanghai",
    "MessageId": "7F3D61FE01E5656C7F9D712CF45CA356",
    "Body": {
      "key1": "val1",
      "key2": "val2"
    }
  }
}
```

#### DeleteMessage

**请求**

- `Action`: `string`，服务方法，常量 `DeleteMessage`
- `Queue`: `string`，队列，必填
- `ReceiptHandle`: `string`，删除消息标识

**返回**

```json
{
  "Status": 204,
  "Header": {
    "Server": "AliyunMQS",
    "Date": "Sat, 22 Jan 2022 15:26:12 GMT",
    "Content-Type": "text/xml;charset=utf-8",
    "Connection": "keep-alive",
    "x-mns-version": "2015-06-06",
    "x-mns-request-id": "61EC22143132375E238EDE3B"
  },
  "RequestId": "61EC22143132375E238EDE3B"
}
```

```yaml
case:
  - name: MNSExample
    step:
      - ctx: mns
        req:
          Action: PublishMessage
          Topic: imm-test-hl-mns-topic-shanghai
          MessageBody: hello world
        res:
          Status: 201
      - ctx: mns
        req:
          Action: ReceiveMessage
          Queue: imm-test-hl-mns-queue-shanghai
          WaitSeconds: 10
        res:
          Status: 200
          Body:
            Message: hello world
      - ctx: mns
        req:
          Action: PublishMessage
          Topic: imm-test-hl-mns-topic-shanghai
          Body:
            key1: val1
            key2: val2
        res:
          Status: 201
      - ctx: mns
        req:
          Action: ReceiveMessage
          Queue: imm-test-hl-mns-queue-shanghai
          WaitSeconds: 10
          AutoRelease: false
        res:
          Status: 200
          Body:
            Body:
              key1: val1
              key2: val2
      - ctx: mns
        req:
          Action: DeleteMessage
          Queue: imm-test-hl-mns-queue-shanghai
          "#ReceiptHandle": "case.steps[3].res['ReceiptHandle']"
        res:
          Status: 204
```
