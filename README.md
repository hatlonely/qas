# qas

一个适合 devops 使用的功能测试框架

## 安装

### 源码安装

```shell
git fetch --depth 1 --branch master https://github.com/hatlonely/qas.git && \
cd qas && \
python3 setup.py install
```

## 快速入门

1. 创建测试文件 [sample.yaml](ops/sample-simple/sample.yaml)

```yaml
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

setUp:
  - name: EchoHelloWorld
    step:
      - ctx: shell
        req:
          command: "echo hello world"

tearDown:
  - name: GoodBye
    step:
      - ctx: shell
        req:
          command: "echo good bye"

case:
  - name: TestHttpJson
    step:
      - ctx: jsontest
        req:
          path: /key/value/one/two
        res:
          status: 200
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
            "#X-Cloud-Trace-Context": "len(val) == 32"
          }
          json: {
            "one": "two",
            "key": "value"
          }
```

2. 执行测试

```shell
qas --test sample.yaml
```

## 背景

在微服务架构的大背景下，一个服务可能会依赖大量的其他服务，而这些服务其实是作为一个整体对外提供服务，大部分业务的请求都会带来后端服务状态的变化，
并不是所有的变化都能通过业务请求获取，事实上大部分服务的状态是不会也没有必要通过 api 提供给业务方，这里举两个典型的例子

1. 计费功能，一般的业务系统里面，计费逻辑的变化一般不会影响业务功能，所以在最外层业务看来，功能上不会有任何变化
2. 任务类功能，提供任务的提交，查询功能，但是任务的产出在其他系统，比如视频转码任务，在 api 侧看起来都成功了，
   但是最终在 oss 侧是否真的有转码文件生成，生成的转码文件的命名，格式，大小，是否都是符合预期的，单从 api 侧是无法知道的
3. 一个健壮的服务会有很多额外的 fallback 策略，这些策略让我们看不到服务内部的异常，仅从接口的返回无法判断服务的正确性

这些不符合预期的服务状态，其实最终都会造成严重的业务影响，**如何在测试阶段发现这些不符合预期的状态变化**，是质量保证的关键。

另一个问题，在测试中有一些异常或者边界是难以构造或者代价很高，比如

1. 用户配额，假如用户使用我们的存储达到 100T 的时候会触发一个限额的逻辑，会给用户返回一个提示，如果要构造 100T 的数据代价会非常高
2. 凭证过期，假如通过某个 api 给用户颁发的凭证会在 7 天后过期，我们几乎不可能让一个测试 7 天后去校验这个凭证是否失效

**如何方便地构建边界和异常**，也是一个很重要的问题。

除此之外，业务方调用我们的服务往往是基于某种具体的场景，以文档转换任务为例，客户使用的典型场景是：

1. 提交文档转换任务
2. 循环获取任务状态，直到任务完成
3. 获取转换后的文档，进行后面的业务逻辑

这个场景里面涉及了多个 api 的连续调用，除了要保证每个 api 在每次调用都符合预期之外，还需要保证在返回任务完成之时，任务是真正完成了，即有对应的转换文档产生

事实上每个业务需求都可以抽象成一个场景，线上的问题也都是在某种特定的场景下触发的问题，如何保证现有的代码不影响已有的功能，
如何保证之前出现过的线上问题不会再次发生，**将这些场景沉淀成可以反复执行的代码**尤其重要。

上面说的问题，其实只是站在两个不同的角度，一个是系统开发的角度，一个是系统使用的角度。在系统开发方面，我们更关注系统实现的细节，
在系统使用方面，我们更关注系统使用的场景。两个角度虽然关注点有所侧重，但其本质都是对接口的调用和结果的校验，这也是这个工具设计的基础。

## 设计目标

1. 系统状态校验
2. 场景测试
3. 使用简单，可以方便地构造 case
4. 方便调试，可以跑单个 case，测试结果清晰
5. 测试报告，支持多种报告格式
6. 可拓展性，报告形式拓展，支持服务拓展，报告拓展

## 特性

1. 全局变量引用，运行结果引用
2. 断言，比较断言，python 断言
3. case/step 条件执行
4. 执行 hook，setup/teardown/before_case/after_case
5. 信息统计，case/step/assertion/elapse
6. retry/until 重试和等待
7. 可拓展的 drivers，目前支持 http/shell/redis/mysql/pop/ots/mns
8. 可拓展的 reporters，目前支持 text/json


## ops 命令

```shell
ops --variable .cfg/dev.yaml --env dev -a run --task sample-simple
ops --variable .cfg/dev.yaml --env dev -a run --task sample-recommend
```
