## shell

shell 可以用来执行命令和脚本

### 启动参数

- `shebang`: `string`，执行程序，默认 `/bin/bash`
- `args`: `[string]`，程序启动参数，默认 `["-c"]`

```yaml
ctx:
  sh:
    type: shell
    dft:
      req:
        envs:
          SH_CTX_ENV_KEY: sh-ctx-env-val
  py:
    type: shell
    args:
      shebang: /usr/local/bin/python3
      args:
        - -c
```

### 执行命令

**请求**

- `command`: `string`，执行命令，必填
- `envs`: `[string, string]`，程序执行环境变量，默认为空
- `decoder`: `string`，解码规则，将结果按某种规则解析成对象，方便后面的结果校验和引用，可选值 `text/json/yaml`，默认 `text`

**返回**

- `exitCode`: 状态返回码
- `stdout`: 标准输出
- `stderr`: 标准错误
- `json`: 如果设置了 decoder，并且格式正确，会将结果转换成对象
- `err`: 如果设置了 decoder，捕获解析失败的异常

```yaml
case:
  - name: ShellExample
    step:
      - ctx: sh
        req:
          command: |
            echo SH_CTX_ENV_KEY=${SH_CTX_ENV_KEY}
            echo CASE_ENV_KYE=${CASE_ENV_KYE}
          envs:
            CASE_ENV_KYE: case-env-val
        res:
          exitCode: 0
          stdout: |
            SH_CTX_ENV_KEY=sh-ctx-env-val
            CASE_ENV_KYE=case-env-val
      - ctx: py
        req:
          command: |
            import json
            print(json.dumps({"key1": "val1", "key2": "val2"}))
          decoder: json
        res:
          exitCode: 0
          stdout: |
              {"key1": "val1", "key2": "val2"}
          stderr: ""
          json:
            key1: val1
            key2: val2
```
