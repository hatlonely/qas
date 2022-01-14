name: sample

ctx:
  imm:
    type: pop
    args:
      AccessKeyId: ${POP_AK}
      AccessKeySecret: ${POP_SK}
      Endpoint: ${POP_ENDPOINT}
      Method: POST
      ProductId: immv2