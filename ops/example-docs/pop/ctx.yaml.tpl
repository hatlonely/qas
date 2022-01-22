name: pop example

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
