## oss

### 启动参数

- `Endpoint`: `string`，服务地址，必填
- `AccessKeyId`: `string`，阿里云访问凭证 id，必填
- `AccessKeySecret`: `string`，阿里云访问凭证 secret，必填
- `Bucket`: `string`，桶

```yaml
ctx:
  oss:
    type: oss
    args:
      AccessKeyId: ${OSS_AK}
      AccessKeySecret: ${OSS_SK}
      Endpoint: ${OSS_ENDPOINT}
      Bucket: ${OSS_BUCKET}
```

### 发起请求

#### PutObjectFromFile

上传文件

**请求**

- `Action`: `string`，服务方法，`PutObjectFromFile`
- `Key`: `string`，oss 文件 key
- `Filename`: `string`，本地文件路径
- `Headers`: `[string, string]`，请求头，默认为空

**返回**

```json
{
  "Status": 200,
  "Headers": {
    "Server": "AliyunOSS",
    "Date": "Sat, 22 Jan 2022 14:23:16 GMT",
    "Content-Length": "0",
    "Connection": "keep-alive",
    "x-oss-request-id": "61EC13546816B73337CBA412",
    "ETag": "\"86D3F3A95C324C9479BD8986968F4327\"",
    "x-oss-hash-crc64ecma": "15881541407605718253",
    "Content-MD5": "htPzqVwyTJR5vYmGlo9DJw==",
    "x-oss-version-id": "CAEQJRiBgMDjg9eI9BciIDVkYWMzZGVmYjMxZTRmOTM4MWI3YjFhNGQwZGNmMzNl",
    "x-oss-server-time": "118"
  },
  "RequestId": "61EC13546816B73337CBA412",
  "Etag": "86D3F3A95C324C9479BD8986968F4327",
  "VersionId": "CAEQJRiBgMDjg9eI9BciIDVkYWMzZGVmYjMxZTRmOTM4MWI3YjFhNGQwZGNmMzNl",
  "DeleteMarker": null
}
```

#### GetObjectToFile

下载文件

**请求**

- `Action`: `string`，服务方法，`GetObjectToFile`
- `Key`: `string`，oss 文件 key
- `Filename`: `string`，本地文件路径
- `Headers`: `[string, string]`，请求头，默认为空
- `Params`: `[string, string]`，Query 参数，默认为空

**返回**

```json
{
  "Status": 200,
  "Headers": {
    "Server": "AliyunOSS",
    "Date": "Sat, 22 Jan 2022 14:23:17 GMT",
    "Content-Type": "application/octet-stream",
    "Content-Length": "11357",
    "Connection": "keep-alive",
    "x-oss-request-id": "61EC13556816B7333742A512",
    "Accept-Ranges": "bytes",
    "ETag": "\"86D3F3A95C324C9479BD8986968F4327\"",
    "Last-Modified": "Sat, 22 Jan 2022 14:23:16 GMT",
    "x-oss-object-type": "Normal",
    "x-oss-hash-crc64ecma": "15881541407605718253",
    "x-oss-storage-class": "Standard",
    "x-oss-expiration": "expiry-date=\"Sun, 23 Jan 2022 00:00:00 GMT\", rule-id=\"501b302a-b8e0-4df7-baad-c951f3d0c3b6\"",
    "x-oss-version-id": "CAEQJRiBgMDjg9eI9BciIDVkYWMzZGVmYjMxZTRmOTM4MWI3YjFhNGQwZGNmMzNl",
    "Content-MD5": "htPzqVwyTJR5vYmGlo9DJw==",
    "x-oss-server-time": "8"
  },
  "RequestId": "61EC13556816B7333742A512",
  "Etag": "86D3F3A95C324C9479BD8986968F4327",
  "ContentLength": 11357,
  "LastModified": 1642861396,
  "VersionId": "CAEQJRiBgMDjg9eI9BciIDVkYWMzZGVmYjMxZTRmOTM4MWI3YjFhNGQwZGNmMzNl",
  "DeleteMarker": null
}
```

#### GetObjectMeta

获取文件元信息

**请求**

- `Action`: `string`，服务方法，`GetObjectToFile`
- `Key`: `string`，oss 文件 key
- `Headers`: `[string, string]`，请求头，默认为空
- `Params`: `[string, string]`，Query 参数，默认为空

**返回**

```json
{
  "Status": 200,
  "Headers": {
    "Server": "AliyunOSS",
    "Date": "Sat, 22 Jan 2022 14:23:17 GMT",
    "Content-Length": "11357",
    "Connection": "keep-alive",
    "x-oss-request-id": "61EC13556816B7333786A512",
    "ETag": "\"86D3F3A95C324C9479BD8986968F4327\"",
    "x-oss-hash-crc64ecma": "15881541407605718253",
    "Last-Modified": "Sat, 22 Jan 2022 14:23:16 GMT",
    "x-oss-version-id": "CAEQJRiBgMDjg9eI9BciIDVkYWMzZGVmYjMxZTRmOTM4MWI3YjFhNGQwZGNmMzNl",
    "x-oss-server-time": "2"
  },
  "RequestId": "61EC13556816B7333786A512",
  "Etag": "86D3F3A95C324C9479BD8986968F4327",
  "ContentLength": 11357,
  "LastModified": 1642861396,
  "VersionId": "CAEQJRiBgMDjg9eI9BciIDVkYWMzZGVmYjMxZTRmOTM4MWI3YjFhNGQwZGNmMzNl",
  "DeleteMarker": null
}
```

#### SignURL

获取文件下载地址

**请求**

- `Action`: `string`，服务方法，`SignURL`
- `Key`: `string`，oss 文件 key
- `Headers`: `[string, string]`，请求头，默认为空
- `Params`: `[string, string]`，Query 参数，默认为空
- `Expires`: `int`，过期时间，单位秒，默认 1800
- `SlashSafe`: `bool`，默认 false

**返回**

- `DownloadURL`: `string`，下载链接

```yaml
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
```
