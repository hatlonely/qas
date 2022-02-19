#!/usr/bin/env python3


import copy
import itertools
import re
import time
import yaml
import traceback
import os
import json
import importlib
import sys
import pathlib
from types import SimpleNamespace
from datetime import datetime
from dataclasses import dataclass
import concurrent.futures
from itertools import repeat
from pathlib import Path


from ..driver import driver_map, Driver
from ..reporter import reporter_map
from ..hook import hook_map, Hook
from ..assertion import expect, check
from ..util import render, merge, REQUIRED
from ..result import TestResult, CaseResult, StepResult, SubStepResult
from .retry_until import Retry, Until, RetryError, UntilError
from .generate import generate_req, generate_res, calculate_num, grouper


@dataclass
class RuntimeConstant:
    test_directory: str
    case_directory: str
    case_regex: str
    case_name: str
    case_id: str
    skip_set_up: bool
    skip_tear_down: bool
    parallel: bool
    x: str


@dataclass
class RuntimeContext:
    ctx: dict[str, Driver]
    var: SimpleNamespace
    var_info: dict
    dft: dict
    common_step_info: dict
    before_case_info: list
    after_case_info: list
    driver_map: dict
    x: any
    hooks: list[Hook]
    step_pool: concurrent.futures.ThreadPoolExecutor
    case_pool: concurrent.futures.ThreadPoolExecutor
    test_pool: concurrent.futures.ThreadPoolExecutor


class Framework:
    constant: RuntimeConstant

    def __init__(
        self,
        test_directory=None,
        case_directory=None,
        case_name=None,
        case_id=None,
        case_regex=None,
        skip_set_up=False,
        skip_tear_down=False,
        reporter="text",
        x=None,
        json_result=None,
        parallel=False,
        step_pool_size=None,
        case_pool_size=None,
        test_pool_size=None,
        hook=None,
        customize=None,
        lang=None,
    ):
        self.step_pool = None
        self.case_pool = None
        self.test_pool = None
        if parallel:
            self.step_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=step_pool_size) if step_pool_size else concurrent.futures.ThreadPoolExecutor()
            self.case_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=case_pool_size) if case_pool_size else concurrent.futures.ThreadPoolExecutor()
            self.test_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=test_pool_size) if test_pool_size else concurrent.futures.ThreadPoolExecutor()

        test_directory = test_directory.strip().rstrip("/") if test_directory else test_directory
        self.constant = RuntimeConstant(
            test_directory=test_directory,
            case_directory=test_directory if not case_directory else os.path.join(test_directory, case_directory.strip().rstrip("/")),
            case_regex=case_regex,
            case_name=case_name,
            case_id=case_id,
            skip_set_up=skip_set_up,
            skip_tear_down=skip_tear_down,
            parallel=parallel,
            x=x,
        )
        self.reporter_map = reporter_map
        self.driver_map = driver_map
        self.hook_map = hook_map
        self.x = None
        if x:
            self.x = Framework.load_x(x)
            if hasattr(self.x, "reporter_map"):
                self.reporter_map = self.reporter_map | self.x.reporter_map
            if hasattr(self.x, "driver_map"):
                self.driver_map = self.driver_map | self.x.driver_map
            if hasattr(self.x, "hook_map"):
                self.hook_map = self.hook_map | self.x.hook_map

        if not customize and os.path.exists("{}/.qas/customize.yaml".format(Path.home())):
            customize = "{}/.qas/customize.yaml".format(Path.home())

        hooks = hook.split(",") if hook else []
        cfg = {}
        if customize:
            with open(customize, "r", encoding="utf-8") as fp:
                cfg = yaml.safe_load(fp)
        cfg = merge(cfg, {
            "i18n": {},
            "reporter": {
                reporter: {
                    "i18n": {}
                },
            },
            "hook": dict([(i, {
                "i18n": {}
            }) for i in hooks]),
            "framework": {
                "keyPrefix": {
                    "eval": "#",
                    "exec": "%",
                    "loop": "!"
                },
                "loadingFiles": {
                    "ctx": "ctx.yaml",
                    "var": "var.yaml",
                    "setUp": "set_up.yaml",
                    "tearDown": "tear_down.yaml",
                    "beforeCase": "before_case.yaml",
                    "afterCase": "after_case.yaml",
                    "commonStep": "common_step.yaml",
                    "description": "README.md",
                }
            }
        })

        if "i18n" in cfg:
            cfg["reporter"][reporter] = merge(cfg["reporter"][reporter], cfg["i18n"])
            for key in hooks:
                cfg["hook"][key] = merge(cfg["hook"][key], cfg["i18n"])
        if lang:
            cfg["reporter"][reporter]["lang"] = lang
            for key in hooks:
                cfg["hook"][key]["lang"] = lang

        self.customize = json.loads(json.dumps(cfg["framework"]), object_hook=lambda y: SimpleNamespace(**y))

        self.reporter = self.reporter_map[reporter](cfg["reporter"][reporter])
        self.hooks = [self.hook_map[i](cfg["hook"][i]) for i in hooks]

        self.json_result = json_result

    def format(self):
        res = TestResult.from_json(json.load(open(self.json_result)))
        print(self.reporter.report(res))

    def run(self):
        rctx = RuntimeContext(
            ctx={},
            dft={},
            var_info={},
            var=None,
            common_step_info={},
            before_case_info=[],
            after_case_info=[],
            driver_map=self.driver_map,
            x=self.x,
            hooks=self.hooks,
            step_pool=self.step_pool,
            case_pool=self.case_pool,
            test_pool=self.test_pool,
        )

        res = self.must_run_test(self.constant.test_directory, self.customize, self.constant, rctx)
        print(self.reporter.report(res))

        for hook in self.hooks:
            hook.on_exit(res)

        return res.is_pass

    @staticmethod
    def must_run_test(
        directory: str,
        customize,
        constant: RuntimeConstant,
        rctx: RuntimeContext,
    ):
        for hook in rctx.hooks:
            hook.on_test_start(directory)
        try:
            result = Framework.run_test(directory, customize, constant, rctx)
        except Exception as e:
            result = TestResult(directory, directory, "", "Exception {}".format(traceback.format_exc()))
        for hook in rctx.hooks:
            hook.on_test_end(result)
        return result

    @staticmethod
    def run_test(
        directory: str,
        customize,
        constant: RuntimeConstant,
        parent_rctx: RuntimeContext,
    ):
        if constant.case_id and not (constant.case_directory + "/").startswith(directory + "/"):
            return TestResult(directory, directory[len(constant.test_directory)+1:], "", is_skip=True)
        if not (constant.case_directory + "/").startswith(directory + "/") and \
                not (directory + "/").startswith(constant.case_directory + "/"):
            return TestResult(directory, directory[len(constant.test_directory)+1:], "", is_skip=True)

        now = datetime.now()

        info = Framework.load_ctx(os.path.basename(directory), "{}/{}".format(directory, customize.loadingFiles.ctx))
        description = info["description"] + Framework.load_description("{}/{}".format(directory, customize.loadingFiles.description))
        var_info = copy.deepcopy(parent_rctx.var_info) | info["var"] | Framework.load_var("{}/{}".format(directory, customize.loadingFiles.var))
        var = json.loads(json.dumps(var_info), object_hook=lambda x: SimpleNamespace(**x))
        common_step_info = copy.deepcopy(parent_rctx.common_step_info) | info["commonStep"] | Framework.load_common_step("{}/{}".format(directory, customize.loadingFiles.commonStep))
        before_case_info = copy.deepcopy(parent_rctx.before_case_info) + info["beforeCase"] + list(Framework.load_step("{}/{}".format(directory, customize.loadingFiles.beforeCase)))
        after_case_info = info["afterCase"] + list(Framework.load_step("{}/{}".format(directory, customize.loadingFiles.afterCase))) + copy.deepcopy(parent_rctx.after_case_info)
        ctx = copy.copy(parent_rctx.ctx)
        dft = copy.deepcopy(parent_rctx.dft)
        for key in info["ctx"]:
            val = merge(info["ctx"][key], {
                "type": REQUIRED,
                "args": {},
                "dft": {
                    "req": {},
                    "retry": {
                        "attempts": 1,
                        "delay": "1s",
                    },
                    "until": {
                        "cond": "",
                        "attempts": 5,
                        "delay": "1s",
                    },
                },
            })
            val = render(val, var=var, x=parent_rctx.x, peval=customize.keyPrefix.eval, pexec=customize.keyPrefix.exec)
            ctx[key] = parent_rctx.driver_map[val["type"]](val["args"])
            dft[key] = val["dft"]

        test_result = TestResult(directory, info["name"], description)

        rctx = RuntimeContext(
            ctx=ctx,
            var=var,
            var_info=var_info,
            dft=dft,
            common_step_info=common_step_info,
            before_case_info=before_case_info,
            after_case_info=after_case_info,
            driver_map=driver_map,
            x=parent_rctx.x,
            hooks=parent_rctx.hooks,
            step_pool=parent_rctx.step_pool,
            case_pool=parent_rctx.case_pool,
            test_pool=parent_rctx.test_pool,
        )

        # 执行 set_up
        if not constant.skip_set_up:
            if not constant.parallel:
                for case_info in Framework.set_ups(customize, info, directory):
                    result = Framework.must_run_case(directory, customize, constant, rctx, case_info, case_type="set_up")
                    test_result.add_set_up_result(result)
            else:
                # 并发执行，每次执行 ctx.yaml 中 parallel.setUp 定义的个数
                for i in grouper(Framework.set_ups(customize, info, directory), info["parallel"]["setUp"]):
                    results = parent_rctx.case_pool.map(
                        Framework.must_run_case,
                        repeat(directory), repeat(customize), repeat(constant), repeat(rctx), i, repeat("set_up")
                    )
                    for result in results:
                        test_result.add_set_up_result(result)
            if not test_result.is_pass:
                return test_result

        # 执行 case
        if directory.startswith(constant.case_directory):
            if not constant.parallel:
                for case_info in Framework.cases(customize, constant, info, directory):
                    result = Framework.must_run_case(directory, customize, constant, rctx, case_info)
                    test_result.add_case_result(result)
            else:
                # 并发执行，每次执行 ctx.yaml 中 parallel.case 定义的个数
                for i in grouper(Framework.cases(customize, constant, info, directory), info["parallel"]["case"]):
                    results = parent_rctx.case_pool.map(
                        Framework.must_run_case,
                        repeat(directory), repeat(customize), repeat(constant), repeat(rctx), i
                    )
                    for result in results:
                        test_result.add_case_result(result)

        # 执行子目录
        if not constant.parallel:
            for sub_directory in [os.path.join(directory, i) for i in os.listdir(directory) if os.path.isdir(os.path.join(directory, i))]:
                result = Framework.must_run_test(sub_directory, customize, constant, rctx)
                test_result.add_sub_test_result(result)
        else:
            # 并发执行，每次执行 ctx.yaml 中 parallel.subTest 定义的个数
            # 每次执行会递归地使用 test_pool，每层目录需要占用一个线程，当 pool size 小于目录嵌套层数时会导致死锁
            # 不设置 test-pool-size 或者设置 test-pool-size 大于最大嵌套层数可解决这个问题
            for directories in grouper([
                os.path.join(directory, i)
                for i in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, i))
            ], info["parallel"]["subTest"]):
                results = parent_rctx.test_pool.map(
                    Framework.must_run_test, directories, repeat(customize), repeat(constant), repeat(rctx),
                )
                for result in results:
                    test_result.add_sub_test_result(result)

        # 执行 tear_down
        if not constant.skip_tear_down:
            if not constant.parallel:
                for case_info in Framework.tear_downs(customize, info, directory):
                    result = Framework.must_run_case(directory, customize, constant, rctx, case_info, case_type="tear_down")
                    test_result.add_tear_down_result(result)
            else:
                # 并发执行，每次执行 ctx.yaml 中 parallel.tearDown 定义的个数
                for i in grouper(Framework.tear_downs(customize, info, directory), info["parallel"]["tearDown"]):
                    results = parent_rctx.case_pool.map(
                        Framework.must_run_case,
                        repeat(directory), repeat(customize), repeat(constant), repeat(rctx), i, repeat("tear_down")
                    )
                    for result in results:
                        test_result.add_tear_down_result(result)

        test_result.elapse = datetime.now() - now
        return test_result

    @staticmethod
    def need_skip(constant, case, var, case_type):
        if case_type == "set_up" or case_type == "tear_down":
            return False
        if constant.case_name and constant.case_name != case["name"]:
            return True
        if constant.case_regex and not re.search(constant.case_regex, case["name"]):
            return True
        if "cond" in case and case["cond"] and not check(case["cond"], var=var):
            return True
        return False

    @staticmethod
    def set_ups(customize, info, directory):
        for case in info["setUp"]:
            yield case
        if os.path.isfile("{}/{}".format(directory, customize.loadingFiles.setUp)):
            for case in Framework.load_case(directory, customize.loadingFiles.setUp):
                yield case

    @staticmethod
    def tear_downs(customize, info, directory):
        for case in info["tearDown"]:
            yield case
        if os.path.isfile("{}/{}".format(directory, customize.loadingFiles.tearDown)):
            for case in Framework.load_case(directory, customize.loadingFiles.tearDown):
                yield case

    @staticmethod
    def cases(customize, constant: RuntimeConstant, info, directory):
        if constant.case_id:
            pos = constant.case_id.find("-")
            if pos == -1:
                filename = constant.case_id + ".yaml"
                idx = 0
            else:
                filename = constant.case_id[:pos] + ".yaml"
                idx = int(constant.case_id[pos+1:])
            if filename == customize.loadingFiles.ctx:
                yield Framework.format_case(info["case"][idx], filename, idx)
            else:
                yield Framework.format_case(list(Framework.load_case(directory, filename))[idx], filename, idx)
            return

        for idx, case in enumerate(info["case"]):
            yield Framework.format_case(case, customize.loadingFiles.ctx, idx)

        for filename in [
            i
            for i in os.listdir(directory)
            if i not in [
                customize.loadingFiles.ctx,
                customize.loadingFiles.var,
                customize.loadingFiles.setUp,
                customize.loadingFiles.tearDown,
                customize.loadingFiles.beforeCase,
                customize.loadingFiles.afterCase,
                customize.loadingFiles.commonStep,
            ]
            and os.path.isfile(os.path.join(directory, i))
        ]:
            if not filename.endswith(".yaml"):
                continue
            for case in Framework.load_case(directory, filename):
                yield case

    @staticmethod
    def load_x(filename):
        if not os.path.exists(filename) or not os.path.isdir(filename):
            return {}
        p = pathlib.Path(filename)
        sys.path.append(str(p.parent.absolute()))
        return importlib.import_module(str(p.name), "x")

    @staticmethod
    def load_var(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return {}
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
        return info

    @staticmethod
    def load_description(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return ""
        with open(filename, "r", encoding="utf-8") as fp:
            info = fp.readlines()
        return info

    @staticmethod
    def load_ctx(name, filename):
        dft = {
            "name": name,
            "description": "",
            "parallel": {
                "case": 0,
                "subTest": 0,
                "setUp": 0,
                "tearDown": 0,
            },
            "ctx": {},
            "var": {},
            "case": [],
            "setUp": [],
            "tearDown": [],
            "beforeCase": [],
            "afterCase": [],
            "commonStep": {},
        }
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return dft
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
        return merge(info, dft)

    @staticmethod
    def load_case(directory, filename):
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if isinstance(info, dict):
                yield Framework.format_case(info, filename, 0)
            if isinstance(info, list):
                for idx, item in enumerate(info):
                    yield Framework.format_case(item, filename, idx)

    @staticmethod
    def format_case(info, filename, idx):
        text = os.path.splitext(filename)[0]
        case_id = "{}-{}".format(text, idx)
        if idx == 0 and text.find("-") == -1:
            case_id = text
        info = merge(info, {
            "name": REQUIRED,
            "description": "",
            "cond": "",
            "caseID": case_id
        })
        return info

    @staticmethod
    def load_step(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return []
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if not info:
                return []
            for step in info:
                yield step

    @staticmethod
    def load_common_step(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return {}
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if not info:
                return {}
        return info

    @staticmethod
    def must_run_case(directory, customize, constant: RuntimeConstant, rctx: RuntimeContext, case_info, case_type="case"):
        case_info = merge(case_info, {
            "name": REQUIRED,
            "description": "",
            "cond": "",
            "label": {},
            "preStep": [],
            "postStep": [],
        })

        for hook in rctx.hooks:
            if case_type == "set_up":
                hook.on_set_up_start(case_info)
            elif case_type == "tear_down":
                hook.on_tear_down_start(case_info)
            else:
                hook.on_case_start(case_info)
        result = Framework.run_case(directory, customize, constant, rctx, case_info, case_type=case_type)
        for hook in rctx.hooks:
            if case_type == "set_up":
                hook.on_set_up_end(result)
            elif case_type == "tear_down":
                hook.on_tear_down_end(result)
            else:
                hook.on_case_end(result)
        return result

    @staticmethod
    def run_case(directory, customize, constant: RuntimeConstant, rctx: RuntimeContext, case_info, case_type="case"):
        if Framework.need_skip(constant, case_info, rctx.var, case_type):
            return CaseResult(directory=directory, id_=case_info["caseID"], name=case_info["name"], is_skip=True)

        command = ""
        case_id = ""
        if case_type == "case":
            case_id = case_info["caseID"]
            if constant.x:
                command = 'qas -x "{}" -t "{}" -c "{}" --case-id "{}"'.format(
                    constant.x, constant.test_directory, directory[len(constant.test_directory) + 1:], case_id,
                )
            else:
                command = 'qas -t "{}" -c "{}" --case-id "{}"'.format(
                    constant.test_directory, directory[len(constant.test_directory) + 1:], case_id,
                )
        case = CaseResult(directory=directory, id_=case_id, name=case_info["name"], description=case_info["description"], command=command)

        now = datetime.now()

        if case_type == "case":
            for idx, step_info, case_add_step_func in itertools.chain([list(i) + [case.add_before_case_step_result] for i in enumerate(rctx.before_case_info)]):
                step = Framework.must_run_step(customize, constant, rctx, step_info, case)
                case_add_step_func(step)
                if not step.is_pass:
                    break
            if not case.is_pass:
                return case

        for idx, step_info, case_add_step_func in itertools.chain(
            [list(i) + [case.add_case_pre_step_result] for i in enumerate([rctx.common_step_info[i] for i in case_info["preStep"]])],
            [list(i) + [case.add_case_step_result] for i in enumerate(case_info["step"])],
            [list(i) + [case.add_case_post_step_result] for i in enumerate([rctx.common_step_info[i] for i in case_info["postStep"]])],
        ):
            step = Framework.must_run_step(customize, constant, rctx, step_info, case)
            case_add_step_func(step)
            if not step.is_pass:
                break

        if case_type == "case":
            for idx, step_info, case_add_step_func in itertools.chain([list(i) + [case.add_after_case_step_result] for i in enumerate(rctx.after_case_info)]):
                step = Framework.must_run_step(customize, constant, rctx, step_info, case)
                case_add_step_func(step)
                if not step.is_pass:
                    break

        case.elapse = datetime.now() - now
        return case

    @staticmethod
    def must_run_step(customize, constant: RuntimeConstant, rctx: RuntimeContext, step_info, case):
        step_info = merge(step_info, {
            "name": "",
            "description": "",
            "parallel": 0,
            "res": {},
            "retry": {},
            "until": {},
            "cond": "",
        })

        for hook in rctx.hooks:
            hook.on_step_start(step_info)
        step = Framework.run_step(customize, constant, rctx, step_info, case)
        for hook in rctx.hooks:
            hook.on_step_end(step)
        return step

    @staticmethod
    def run_step(customize, constant, rctx, step_info, case):
        # 条件步骤
        if step_info["cond"] and not check(step_info["cond"], case=case, var=rctx.var, x=rctx.x):
            return StepResult(step_info["name"], step_info["ctx"], is_skip=True)
        step = StepResult(step_info["name"], step_info["ctx"], step_info["description"])
        now = datetime.now()

        mode = ""
        if customize.keyPrefix.eval + "res" in step_info:
            step_info["res"] = step_info[customize.keyPrefix.eval + "res"]
            mode = customize.keyPrefix.eval
        elif customize.keyPrefix.exec + "res" in step_info:
            step_info["res"] = step_info[customize.keyPrefix.exec + "res"]
            mode = customize.keyPrefix.exec
        if not constant.parallel:
            for req, res in zip(
                generate_req(step_info["req"], p=customize.keyPrefix.loop),
                generate_res(step_info["res"], calculate_num(step_info["req"], p=customize.keyPrefix.loop), p=customize.keyPrefix.loop)
            ):
                result = Framework.run_sub_step(customize, rctx, case, req, res, step_info, mode=mode)
                step.add_sub_step_result(result)
        else:
            # 并发执行，每次执行 case.step 中 parallel 定义的个数
            for reqs, ress in zip(
                    grouper(generate_req(step_info["req"], p=customize.keyPrefix.loop), step_info["parallel"]),
                    grouper(generate_res(step_info["res"], calculate_num(step_info["req"], p=customize.keyPrefix.loop), p=customize.keyPrefix.loop), step_info["parallel"])
            ):
                results = rctx.step_pool.map(
                    Framework.run_sub_step,
                    repeat(customize), repeat(rctx), repeat(case), reqs, ress, repeat(step_info), repeat(mode)
                )
                for result in results:
                    step.add_sub_step_result(result)

        # auto name step
        if not step.name:
            step.name = rctx.ctx[step_info["ctx"]].name(step.req)
            if not step.name:
                step.name = "anonymous-step"
        step.elapse = datetime.now() - now
        return step

    @staticmethod
    def run_sub_step(customize, rctx: RuntimeContext, case, req, res, step_info, mode=""):
        sub_step_result = SubStepResult()
        sub_step_start = datetime.now()
        try:
            req = merge(req, rctx.dft[step_info["ctx"]]["req"])
            # use json transform tuple to list
            req = render(json.loads(json.dumps(req)), case=case, var=rctx.var, x=rctx.x, peval=customize.keyPrefix.eval, pexec=customize.keyPrefix.exec)
            sub_step_result.req = req

            retry = Retry(merge(step_info["retry"], rctx.dft[step_info["ctx"]]["retry"]))
            until = Until(merge(step_info["until"], rctx.dft[step_info["ctx"]]["until"]))

            for i in range(until.attempts):
                for j in range(retry.attempts):
                    step_res = rctx.ctx[step_info["ctx"]].do(req)
                    sub_step_result.res = step_res
                    if retry.condition == "" or not check(retry.condition, case=case, step=sub_step_result, var=rctx.var, x=rctx.x):
                        break
                    time.sleep(retry.delay.total_seconds())
                else:
                    raise RetryError()
                if until.condition == "" or check(until.condition, case=case, step=sub_step_result, var=rctx.var, x=rctx.x):
                    break
                time.sleep(until.delay.total_seconds())
            else:
                raise UntilError()

            result = expect(step_res, json.loads(json.dumps(res)), case=case, step=sub_step_result, var=rctx.var, x=rctx.x, peval=customize.keyPrefix.eval, pexec=customize.keyPrefix.exec, mode=mode)
            sub_step_result.add_expect_result(result)
        except RetryError as e:
            sub_step_result.set_error("RetryError [{}]".format(retry))
        except UntilError as e:
            sub_step_result.set_error("UntilError [{}], ".format(until))
        except Exception as e:
            sub_step_result.set_error("Exception {}".format(traceback.format_exc()))
        # ensure req can json serialize
        sub_step_result.req = json.loads(json.dumps(sub_step_result.req, default=lambda y: str(y)))
        sub_step_result.elapse = datetime.now() - sub_step_start
        return sub_step_result
