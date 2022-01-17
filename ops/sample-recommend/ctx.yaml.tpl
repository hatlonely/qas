name: sample

ctx:
  shell:
    type: shell
  jsontest:
    type: http
    args:
      endpoint: http://echo.jsontest.com/
    req:
      method: GET
  imm:
    type: pop
    args:
      AccessKeyId: ${POP_AK}
      AccessKeySecret: ${POP_SK}
      Endpoint: ${POP_ENDPOINT}
      Method: POST
      ProductId: immv2
