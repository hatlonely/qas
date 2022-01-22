name: oss example

ctx:
  oss:
    type: oss
    args:
      AccessKeyId: ${OSS_AK}
      AccessKeySecret: ${OSS_SK}
      Endpoint: ${OSS_ENDPOINT}
      Bucket: ${OSS_BUCKET}

case:
  - name: OSSExample
    step:
      - ctx: oss
        req:
          Action: PutObjectFromFile
          Key: LICENSE
          Filename: LICENSE
        res:
          Status: 200
          Headers:
            Server: AliyunOSS
      - ctx: oss
        req:
          Action: GetObjectToFile
          Key: LICENSE
          Filename: LICENSE
        res:
          Status: 200
          Headers:
            Server: AliyunOSS
      - ctx: oss
        req:
          Action: GetObjectMeta
          Key: LICENSE
        res:
          Status: 200
      - ctx: oss
        req:
          Action: SignURL
          Key: LICENSE
