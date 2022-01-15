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
  rpcTool:
    type: http
    args:
      endpoint: "http://k8s.rpc.tool.hatlonely.com"
      headers:
        Origin: "http://k8s.rpc.tool.hatlonely.com"
      method: POST
