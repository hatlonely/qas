# qas

一个简单的功能测试框架

## 背景

## 设计目标

1. 功能测试
2. 使用简单，可以方便地构造 case
3. 方便调试，可以跑单个 case，测试结果清晰
4. 测试报告，支持多种报告格式
5. 可拓展性，报告形式拓展，支持服务拓展，断言拓展

## ops 命令

```shell
ops --variable .cfg/ali.yaml --env ali -a run --task sample
```
