name: sample

ctx:
  sh:
    type: shell
    args:
      envs:
        SH_CTX_ENV_KEY: sh-ctx-env-val
  py:
    type: shell
    args:
      shebang: /usr/local/bin/python3
      args:
        - -c
      envs:
        PY_CTX_ENV_KEY: py-ctx-env-val
  jsontest:
    type: http
    args:
      endpoint: http://echo.jsontest.com/
    dft:
      req:
        method: GET
        timeout: 10s
  imm:
    type: pop
    args:
      AccessKeyId: ${IMM_AK}
      AccessKeySecret: ${IMM_SK}
      Endpoint: ${IMM_ENDPOINT}
      Method: POST
      ProductId: imm
  ots:
    type: ots
    args:
      AccessKeyId: ${OTS_AK}
      AccessKeySecret: ${OTS_SK}
      Endpoint: ${OTS_ENDPOINT}
      Instance: ${OTS_INSTANCE}
