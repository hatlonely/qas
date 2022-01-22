## pop

pop 是阿里云的网关，很多阿里云产品都通过 pop 提供对外的 api，pop driver 提供统一的阿里云 api 的访问

### 启动参数

- `AccessKeyId`: `string`，阿里云访问凭证 id，必填
- `AccessKeySecret`: `string`，阿里云访问凭证 secret，必填
- `Endpoint`: `string`，阿里云服务地址，默认为空
- `RegionId`: `string`，地区，默认为空

```yaml
ctx:
  imm:
    type: pop
    args:
      AccessKeyId: ${IMM_AK}
      AccessKeySecret: ${IMM_SK}
      Endpoint: ${IMM_ENDPOINT}
    dft:
      req:
        ProductId: imm
```

### 发起请求

**请求**

- `Action`: `string`，调用服务方法，必填
- `Method`: `string`，http 方法，默认 POST
- `ProductId`: `string`，阿里云服务 id，这个字段只是为了服务默认的 api 版本，可不填，直接设置 `Version` 字段，目前支持: `ots/imm/ram/slb/ack/rds/redis/ecs/vpc/kms/sts`
- `Version`: `string`，阿里服务 api 版本
- `RegionId`: `string`，服务地区，默认为空
- `Endpoint`: `string`，服务地址，默认使用启动参数中的 `Endpoint`

其他 api 参数参考具体的 api 文档

**返回**

返回参考具体的 api 文档

**错误**

- `Status`: `int`，http 状态码
- `Code`: `string`，错误码
- `Message`: `string`，错误信息
- `RequestId`: `string`，请求 id

```yaml
case:
  - name: POPExample
    desc: |
      阿里云很多产品的 api 都是通过 pop 对外提供
      以 imm 的文档预览接口为例
      参考: api 文档 <https://help.aliyun.com/document_detail/197407.html>
    step:
      - ctx: imm
        req: {
          "Action": "GetWebofficeURL",
          "Project": "hl-shanghai-doc-project",
          "FileID": "1232",
          "User": "{\"ID\": \"user1\",\"Name\": \"wps-user1\",\"Avatar\": \"http://xxx.cn/?id=user1\"}",
          "Permission": "{\"Rename\": true, \"Readonly\": false, \"History\": true}",
          "File": "[{\"Modifier\": {\"Avatar\": \"http://xxx.cn/?id=user1\", \"ID\": \"user1\", \"Name\": \"wps-user1\"}, \"Name\": \"checklist.pptx\", \"Creator\": {\"Avatar\": \"http://xxx.cn/?id=user1\", \"ID\": \"user1\", \"Name\": \"wps-user1\"}, \"SrcUri\": \"oss://imm-test-hl-shanghai/checklist.pptx\", \"Version\": 3, \"TgtUri\": \"oss://imm-test-hl-shanghai/checklist.pptx\"}]",
          "NotifyEndpoint": "",
          "NotifyTopicName": "",
          "Watermark": "{\"Rotate\": -0.7853982, \"Vertical\": 100, \"Value\": \"hatlonely\", \"FillStyle\": \"rgba(192, 192, 192, 0.6)\", \"Horizontal\": 50, \"Font\": \"bold 20px Serif\", \"Type\": 1}",
          "Hidecmb": "false"
        }
        res: {
          "WebofficeURL": "https://office-cn-shanghai.imm.aliyuncs.com/office/p/ecfecdbe530a9a80a4bc4352e15ebdd8e8a27875?_w_tokentype=1",
          "#RefreshToken": "len(val) == 34 and val.endswith('v3')",
          "#AccessToken": "len(val) == 34 and val.endswith('v3')",
          "#RefreshTokenExpiredTime": "86350 < (to_time(val) - datetime.now(timezone.utc)).total_seconds() < 86450",
          "#AccessTokenExpiredTime": "1750 < (to_time(val) - datetime.now(timezone.utc)).total_seconds() < 1850",
          "#RequestId": "len(val) == 36",
        }
```

