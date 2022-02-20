# qas

一个通用、并发、可拓展的功能测试框架

## 安装

### pip 安装

```shell
pip3 install qas
```

### 源码安装

```shell
git fetch --depth 1 --branch master https://github.com/hatlonely/qas.git && \
cd qas && \
python3 setup.py install && \
python3 -m pip install -r requirements.txt
```

### docker 运行

```shell
docker run -i --tty --rm \
  -v $(pwd)/ops/example-docs/helloworld:/example-docs/helloworld \
  docker.io/hatlonely/qas:1.0.0 qas -t example-docs/helloworld
```

## 快速入门

1. 创建一个 case 文件 `helloworld/ctx.yaml`

```yaml
name: hello-world

ctx:
  shell:
    type: shell

case:
  - name: HelloWorld
    step:
      - ctx: shell
        req:
          command: echo -n hello world
        res:
          exitCode: 0
          stdout: hello world
```

2. 执行测试

```shell
qas --test helloworld
```

更多使用帮助，参考[用户指南](/docs/用户指南)

## 背景

长久以来，在瀑布模型开发，测试，运维分工下，开发人员熟悉整个软件的所有实现细节，而测试人员更关注软件最外层的功能，
而运维人员主要关注系统的稳定性。在质量保证上，开发人员主要负责代码级别的单元测试，测试人员负责系统级别的功能测试。

这样的分工也影响了技术的发展方向，大部分的功能测试框架是面向测试人员甚至更上层的业务人员设计的，目标让测试 case 更接近于自然语言，
这个目标其实需要付出很多额外的成本，在 behave 框架里面，测试人员需要写很多额外的 case 驱动来实现特定业务逻辑的测试，
而自然语言风格的 case 其实对开发人员很不友好，特别是在构造复杂 case 的场景下，自然语言实际上非常难以描述。

随着 devops 研发模式的兴起，开发测试运维职责的统一，对功能测试框架的需求也发生了变化，测试人员不再是只关注于功能专业测试，
同时也是熟悉整个软件实现细节的开发人员，测试框架对自然语言不再有强烈的需求，而对测试开发的效率以及复杂的业务场景的代码化描述有了更强的需求。

qas 就是为了解决 devops 的功能测试问题，通过 yaml 来描述测试的执行过程和结果校验，以驱动的方式拓展服务的后端，自动生成测试报告。

![qas-架构](/docs/assets/qas-架构.png)

## 特性

1. 完全 yaml 描述
2. 变量引用，支持常量引用 `var`，支持运行结果引用 `case/step/val`
3. 断言，支持相等断言，支持 python 断言
4. 支持请求默认值
5. 支持条件执行
6. 支持循环执行
7. 支持执行 hook，`setUp/tearDown/beforeCase/afterCase`
8. 支持公共步骤引用，`preStep/postStep`
9. 支持重试和等待，`retry/until`
10. 测试信息统计，`case/step/assertion` 成功失败数，`elapse` 时间统计
11. 测试报告，支持 `text/json/html`
12. 支持 `http/grpc/thrift/shell/redis/mysql/mongo/pop/ots/mns/oss`
13. 支持用户 python 拓展
14. 支持并发执行
15. 支持国际化
16. 支持个性化

## ops 命令

```shell
ops --variable .cfg/dev.yaml --env dev -a run --task example-docs
ops --variable .cfg/dev.yaml --env dev -a run --task image
```
