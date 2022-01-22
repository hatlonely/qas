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

#### ReceiveMessage

#### DeleteMessage

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
        res:
          Status: 200
          Body:
            Body:
              key1: val1
              key2: val2
```
