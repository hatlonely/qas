name: ots example

ctx:
  ots:
    type: ots
    args:
      AccessKeyId: ${OTS_AK}
      AccessKeySecret: ${OTS_SK}
      Endpoint: ${OTS_ENDPOINT}
      Instance: ${OTS_INSTANCE}

setUp:
  - name: CreateTable
    step:
      - ctx: ots
        req:
          Action: CreateTable
          TableMeta:
            TableName: TestQAS
            SchemaEntry:
              - Name: PK1
                Type: STRING
              - Name: PK2
                Type: STRING
            TableOptions:
              TimeToLive: -1
              MaxVersion: 1
              MaxTimeDeviation: 86400

tearDown:
  - name: DeleteTable
    step:
      - ctx: ots
        req:
          Action: DeleteTable
          TableName: TestQAS

case:
  - name: OTSExample
    desc: |
      参考: api 文档 <https://help.aliyun.com/document_detail/27303.html>
    step:
      - ctx: ots
        req:
          Action: ListTable
        res:
      - ctx: ots
        req:
          Action: PutRow
          TableName: TestQAS
          Row:
            PrimaryKey:
              - Key: PK1
                Val: pkVal1
              - Key: PK2
                Val: pkVal2
            AttributeColumns:
              key1: val1
              key2: val2
      - ctx: ots
        req:
          Action: GetRow
          TableName: TestQAS
          PrimaryKey:
            - Key: PK1
              Val: pkVal1
            - Key: PK2
              Val: pkVal2
        res:
          key1: val1
          key2: val2
      - ctx: ots
        req:
          Action: GetRange
          TableName: TestQAS
          StartPrimaryKey:
            - Key: PK1
            - Key: PK2
          EndPrimaryKey:
            - Key: PK1
            - Key: PK2
        res:
          - PK1: pkVal1
            PK2: pkVal2
            key1: val1
            key2: val2
      - ctx: ots
        req:
          Action: DeleteRow
          TableName: TestQAS
          PrimaryKey:
            - Key: PK1
              Val: pkVal1
            - Key: PK2
              Val: pkVal2
