name: http-example

ctx:
  mns:
    type: mns
    args:
      AccessKeyId: ${MNS_AK}
      AccessKeySecret: ${MNS_SK}
      Endpoint: ${MNS_ENDPOINT}

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
