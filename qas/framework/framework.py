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

from ..driver import driver_map
from ..reporter import reporter_map
from ..hook import hook_map
from ..assertion import expect, check
from ..util import render, merge, REQUIRED
from ..result import TestResult, CaseResult, StepResult, SubStepResult
from .retry_until import Retry, Until, RetryError, UntilError
from .generate import generate_req, generate_res, calculate_num, grouper


def dict_to_sns(d):
    return SimpleNamespace(**d)


@dataclass
class RuntimeConstant:
    test_directory: str
    case_directory: str
    case_regex: str
    case_name: str
    skip_setup: bool
    skip_teardown: bool
    parallel: bool


class Framework:
    runtime_constant: RuntimeConstant

    def __init__(
        self,
        test_directory=None,
        case_directory=None,
        case_name=None,
        case_regex=None,
        skip_setup=False,
        skip_teardown=False,
        reporter="text",
        x=None,
        json_result=None,
        parallel=False,
        step_pool_size=None,
        case_pool_size=None,
        test_pool_size=None,
        hook=None,
        config=None,
    ):
        self.runtime_constant = RuntimeConstant(
            test_directory=test_directory.rstrip("/"),
            case_directory=test_directory if not case_directory else os.path.join(test_directory, case_directory.rstrip("/")),
            case_regex=case_regex,
            case_name=case_name,
            skip_setup=skip_setup,
            skip_teardown=skip_teardown,
            parallel=parallel,
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

        hooks = hook.split(",") if hook else []
        cfg = {}
        if config:
            with open(config, "r", encoding="utf-8") as fp:
                cfg = yaml.safe_load(fp)
        cfg = merge(cfg, {
            "reporter": {
                reporter: {},
            },
            "hook": dict([(i, {}) for i in hooks]),
        })

        self.reporter = self.reporter_map[reporter](cfg["reporter"][reporter])
        self.hooks = [self.hook_map[i](cfg["hook"][i]) for i in hooks]

        self.json_result = json_result

        self.step_pool = None
        self.case_pool = None
        self.test_pool = None
        if self.runtime_constant.parallel:
            self.step_pool = concurrent.futures.ThreadPoolExecutor(max_workers=step_pool_size) if step_pool_size else concurrent.futures.ThreadPoolExecutor()
            self.case_pool = concurrent.futures.ThreadPoolExecutor(max_workers=case_pool_size) if case_pool_size else concurrent.futures.ThreadPoolExecutor()
            self.test_pool = concurrent.futures.ThreadPoolExecutor(max_workers=test_pool_size) if test_pool_size else concurrent.futures.ThreadPoolExecutor()

    def format(self):
        res = TestResult.from_json(json.load(open(self.json_result)))
        print(self.reporter.report(res))

    def run(self):
        res = self.must_run_test(self.runtime_constant, self.runtime_constant.test_directory, {}, {}, {}, {}, [], [], self.driver_map, self.x, self.hooks, self.step_pool, self.case_pool, self.test_pool)
        print(self.reporter.report(res))
        return res.is_pass

    @staticmethod
    def must_run_test(
        runtime_constant: RuntimeConstant,
        test_directory,
        parent_var_info,
        parent_ctx,
        parent_dft_info,
        parent_common_step_info,
        parent_before_case_info,
        parent_after_case_info,
        parent_drivers,
        parent_x,
        hooks,
        step_pool,
        case_pool,
        test_pool,
    ):
        if not (runtime_constant.case_directory + "/").startswith(test_directory + "/") and not (test_directory + "/").startswith(runtime_constant.case_directory + "/"):
            return TestResult(test_directory, test_directory, "", is_skip=True)
        for hook in hooks:
            hook.on_test_start(test_directory)
        try:
            result = Framework.run_test(
                runtime_constant, test_directory, parent_var_info, parent_ctx, parent_dft_info, parent_common_step_info, parent_before_case_info,
                parent_after_case_info, parent_drivers, parent_x, hooks, step_pool, case_pool, test_pool,
            )
        except Exception as e:
            result = TestResult(test_directory, test_directory, "", "Exception {}".format(traceback.format_exc()))
        for hook in hooks:
            hook.on_test_end(result)
        return result

    @staticmethod
    def run_test(
            runtime_constant: RuntimeConstant,
            test_directory,
            parent_var_info,
            parent_ctx,
            parent_dft_info,
            parent_common_step_info,
            parent_before_case_info,
            parent_after_case_info,
            parent_drivers,
            parent_x,
            hooks,
            step_pool,
            case_pool,
            test_pool,
    ):
        now = datetime.now()
        info = Framework.load_ctx(os.path.basename(test_directory), "{}/ctx.yaml".format(test_directory))
        description = info["description"] + Framework.load_description("{}/README.md".format(test_directory))
        var_info = copy.deepcopy(parent_var_info) | info["var"] | Framework.load_var("{}/var.yaml".format(test_directory))
        var = json.loads(json.dumps(var_info), object_hook=dict_to_sns)
        common_step_info = copy.deepcopy(parent_common_step_info) | info["commonStep"] | Framework.load_common_step("{}/common_step.yaml".format(test_directory))
        before_case_info = copy.deepcopy(parent_before_case_info) + info["beforeCase"] + list(Framework.load_step("{}/before_case.yaml".format(test_directory)))
        after_case_info = copy.deepcopy(parent_after_case_info) + info["afterCase"] + list(Framework.load_step("{}/after_case.yaml".format(test_directory)))
        ctx = copy.copy(parent_ctx)
        dft_info = copy.deepcopy(parent_dft_info)
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
            val = render(val, var=var)
            ctx[key] = parent_drivers[val["type"]](val["args"])
            dft_info[key] = val["dft"]

        test_result = TestResult(test_directory, info["name"], description)

        # 执行 setup
        if not runtime_constant.skip_setup:
            if not runtime_constant.parallel:
                for case_info in Framework.setups(info, test_directory):
                    result = Framework.must_run_case(
                        test_directory, runtime_constant, [], case_info, [], common_step_info, dft_info, var=var, ctx=ctx, x=parent_x,
                        hooks=hooks, step_pool=step_pool, case_type="setup",
                    )
                    test_result.add_setup_result(result)
            else:
                # 并发执行，每次执行 ctx.yaml 中 parallel.setUp 定义的个数
                for i in grouper(Framework.setups(info, test_directory), info["parallel"]["setUp"]):
                    results = case_pool.map(
                        Framework.must_run_case,
                        repeat(test_directory), repeat(runtime_constant), repeat(before_case_info), i, repeat(after_case_info),
                        repeat(common_step_info), repeat(dft_info), repeat(var), repeat(ctx), repeat(parent_x), repeat(hooks),
                        repeat(step_pool), repeat("setup")
                    )
                    for result in results:
                        test_result.add_setup_result(result)
            if not test_result.is_pass:
                return test_result

        # 执行 case
        if test_directory.startswith(runtime_constant.case_directory):
            if not runtime_constant.parallel:
                for case_info in Framework.cases(info, test_directory):
                    result = Framework.must_run_case(test_directory, runtime_constant, before_case_info, case_info, after_case_info, common_step_info, dft_info, var=var, ctx=ctx, x=parent_x, hooks=hooks, step_pool=step_pool)
                    test_result.add_case_result(result)
            else:
                # 并发执行，每次执行 ctx.yaml 中 parallel.case 定义的个数
                for i in grouper(Framework.cases(info, test_directory), info["parallel"]["case"]):
                    results = case_pool.map(
                        Framework.must_run_case,
                        repeat(test_directory), repeat(runtime_constant), repeat(before_case_info), i, repeat(after_case_info),
                        repeat(common_step_info), repeat(dft_info), repeat(var), repeat(ctx), repeat(parent_x), repeat(hooks), repeat(step_pool),
                    )
                    for result in results:
                        test_result.add_case_result(result)

        # 执行子目录
        if not runtime_constant.parallel:
            for directory in [os.path.join(test_directory, i) for i in os.listdir(test_directory) if os.path.isdir(os.path.join(test_directory, i))]:
                result = Framework.must_run_test(runtime_constant, directory, var_info, ctx, dft_info, common_step_info, before_case_info, after_case_info, parent_drivers, parent_x, hooks, step_pool, case_pool, test_pool)
                test_result.add_sub_test_result(result)
        else:
            # 并发执行，每次执行 ctx.yaml 中 parallel.subTest 定义的个数
            # 每次执行会递归地使用 test_pool，每层目录需要占用一个线程，当 pool size 小于目录嵌套层数时会导致死锁
            # 不设置 test-pool-size或者设置 test-pool-size 大于最大嵌套层数可解决这个问题
            for i in grouper([os.path.join(test_directory, i) for i in os.listdir(test_directory) if os.path.isdir(os.path.join(test_directory, i))], info["parallel"]["subTest"]):
                results = test_pool.map(
                    Framework.must_run_test,
                    repeat(runtime_constant),
                    i,
                    repeat(var_info), repeat(ctx), repeat(dft_info), repeat(common_step_info), repeat(before_case_info),
                    repeat(after_case_info),
                    repeat(parent_drivers), repeat(parent_x), repeat(hooks), repeat(step_pool), repeat(case_pool), repeat(test_pool),
                )
                for result in results:
                    test_result.add_sub_test_result(result)

        # 执行 teardown
        if not runtime_constant.skip_teardown:
            if not runtime_constant.parallel:
                for case_info in Framework.teardowns(info, test_directory):
                    result = Framework.must_run_case(test_directory, runtime_constant, [], case_info, [], common_step_info, dft_info, var=var, ctx=ctx, x=parent_x, hooks=hooks, step_pool=step_pool, case_type="teardown")
                    test_result.add_teardown_result(result)
            else:
                # 并发执行，每次执行 ctx.yaml 中 parallel.tearDown 定义的个数
                for i in grouper(Framework.teardowns(info, test_directory), info["parallel"]["tearDown"]):
                    results = case_pool.map(
                        Framework.must_run_case,
                        repeat(test_directory), repeat(runtime_constant), repeat(before_case_info), i, repeat(after_case_info),
                        repeat(common_step_info), repeat(dft_info), repeat(var), repeat(ctx), repeat(parent_x), repeat(hooks),
                        repeat(step_pool), repeat("teardown")
                    )
                    for result in results:
                        test_result.add_teardown_result(result)

        test_result.elapse = datetime.now() - now
        return test_result

    @staticmethod
    def need_skip(runtime_constant, case, var, case_type):
        if case_type == "setup" or case_type == "teardown":
            return False
        if runtime_constant.case_name and runtime_constant.case_name != case["name"]:
            return True
        if runtime_constant.case_regex and not re.search(runtime_constant.case_regex, case["name"]):
            return True
        if "cond" in case and case["cond"] and not check(case["cond"], var=var):
            return True
        return False

    @staticmethod
    def setups(info, test_directory):
        for case in info["setUp"]:
            yield case
        if os.path.isfile("{}/setup.yaml".format(test_directory)):
            for case in Framework.load_case("{}/setup.yaml".format(test_directory)):
                yield case

    @staticmethod
    def teardowns(info, test_directory):
        for case in info["tearDown"]:
            yield case
        if os.path.isfile("{}/teardown.yaml".format(test_directory)):
            for case in Framework.load_case("{}/teardown.yaml".format(test_directory)):
                yield case

    @staticmethod
    def cases(info, test_directory):
        for case in info["case"]:
            yield case

        for filename in [
            os.path.join(test_directory, i)
            for i in os.listdir(test_directory)
            if i not in ["var.yaml", "ctx.yaml", "setup.yaml", "teardown.yaml", "before_case.yaml", "after_case.yaml", "common_step.yaml"]
            and os.path.isfile(os.path.join(test_directory, i))
        ]:
            if not filename.endswith(".yaml"):
                continue
            for case in Framework.load_case(filename):
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
    def load_case(filename):
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if isinstance(info, dict):
                yield Framework.format_case(info)
            if isinstance(info, list):
                for item in info:
                    yield Framework.format_case(item)

    @staticmethod
    def format_case(info):
        info = merge(info, {
            "name": REQUIRED,
            "description": "",
            "cond": "",
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
    def must_run_case(directory, runtime_constant, before_case_info, case_info, after_case_info, common_step_info, dft, var=None, ctx=None, x=None, hooks=None, step_pool=None, case_type="case"):
        for hook in hooks:
            if case_type == "setup":
                hook.on_setup_start(case_info)
            elif case_type == "teardown":
                hook.on_teardown_start(case_info)
            else:
                hook.on_case_start(case_info)
        result = Framework.run_case(
            runtime_constant, directory,
            Framework.need_skip(runtime_constant, case_info, var, case_type), before_case_info, case_info, after_case_info,
            common_step_info, dft, var=var, ctx=ctx, x=x, hooks=hooks, parallel=runtime_constant.parallel, step_pool=step_pool, case_type=case_type
        )
        for hook in hooks:
            if case_type == "setup":
                hook.on_setup_end(result)
            elif case_type == "teardown":
                hook.on_teardown_end(result)
            else:
                hook.on_case_end(result)
        return result

    @staticmethod
    def run_case(runtime_constant, directory, need_skip, before_case_info, case_info, after_case_info, common_step_info, dft, var=None, ctx=None, x=None, hooks=None, parallel=False, step_pool=None, case_type="case"):
        if need_skip:
            return CaseResult(directory=directory, name=case_info["name"], is_skip=True)

        case_info = merge(case_info, {
            "name": REQUIRED,
            "description": "",
            "cond": "",
            "label": {},
            "preStep": [],
            "postStep": [],
        })

        command = ""
        if case_type == "case":
            command = 'qas -t "{}" -c "{}" --case-name "{}"'.format(runtime_constant.test_directory, directory[len(runtime_constant.test_directory) + 1:], case_info["name"])
        case = CaseResult(
            directory=directory, name=case_info["name"], description=case_info["description"],
            command=command,
        )

        now = datetime.now()
        for idx, step_info, case_add_step_func in itertools.chain([list(i) + [case.add_before_case_step_result] for i in enumerate(before_case_info)]):
            step = Framework.must_run_step(step_info, case, dft, var=var, ctx=ctx, x=x, hooks=hooks, parallel=parallel, step_pool=step_pool)
            case_add_step_func(step)
            if not step.is_pass:
                break
        if not case.is_pass:
            return case

        for idx, step_info, case_add_step_func in itertools.chain(
            [list(i) + [case.add_case_pre_step_result] for i in enumerate([common_step_info[i] for i in case_info["preStep"]])],
            [list(i) + [case.add_case_step_result] for i in enumerate(case_info["step"])],
            [list(i) + [case.add_case_post_step_result] for i in enumerate([common_step_info[i] for i in case_info["postStep"]])],
        ):
            step = Framework.must_run_step(step_info, case, dft, var=var, ctx=ctx, x=x, hooks=hooks, parallel=parallel, step_pool=step_pool)
            case_add_step_func(step)
            if not step.is_pass:
                break

        for idx, step_info, case_add_step_func in itertools.chain([list(i) + [case.add_after_case_step_result] for i in enumerate(after_case_info)]):
            step = Framework.must_run_step(step_info, case, dft, var=var, ctx=ctx, x=x, hooks=hooks, parallel=parallel, step_pool=step_pool)
            case_add_step_func(step)
            if not step.is_pass:
                break

        case.elapse = datetime.now() - now
        return case

    @staticmethod
    def must_run_step(step_info, case, dft, var=None, ctx=None, x=None, hooks=None, parallel=False, step_pool=None):
        step_info = merge(step_info, {
            "name": "",
            "description": "",
            "parallel": 0,
            "res": {},
            "retry": {},
            "until": {},
            "cond": "",
        })

        for hook in hooks:
            hook.on_step_start(step_info)
        step = Framework.run_step(step_info, case, dft, var=var, ctx=ctx, x=x, parallel=parallel, step_pool=step_pool)
        for hook in hooks:
            hook.on_step_end(step)
        return step

    @staticmethod
    def run_step(step_info, case, dft, var=None, ctx=None, x=None, parallel=False, step_pool=None):
        # 条件步骤
        if step_info["cond"] and not check(step_info["cond"], case=case, var=var, x=x):
            return StepResult(step_info["name"], step_info["ctx"], is_skip=True)
        step = StepResult(step_info["name"], step_info["ctx"], step_info["description"])
        now = datetime.now()

        if not parallel:
            for req, res in zip(generate_req(step_info["req"]), generate_res(step_info["res"], calculate_num(step_info["req"]))):
                result = Framework.run_sub_step(req, res, step_info, case, dft, var, ctx, x)
                step.add_sub_step_result(result)
        else:
            # 并发执行，每次执行 case.step 中 parallel 定义的个数
            for reqs, ress in zip(
                    grouper(generate_req(step_info["req"]), step_info["parallel"]),
                    grouper(generate_res(step_info["res"], calculate_num(step_info["req"])), step_info["parallel"])
            ):
                results = step_pool.map(
                    Framework.run_sub_step,
                    reqs, ress, repeat(step_info), repeat(case), repeat(dft), repeat(var), repeat(ctx), repeat(x),
                )
                for result in results:
                    step.add_sub_step_result(result)

        # auto name step
        if not step.name:
            step.name = ctx[step_info["ctx"]].default_step_name(step.req)
            if not step.name:
                step.name = "anonymous-step"
        step.elapse = datetime.now() - now
        return step

    @staticmethod
    def run_sub_step(req, res, step_info, case, dft, var, ctx, x):
        sub_step_result = SubStepResult()
        sub_step_start = datetime.now()
        try:
            req = merge(req, dft[step_info["ctx"]]["req"])
            req = render(json.loads(json.dumps(req)), case=case, var=var, x=x)  # use json translate tuple to list
            sub_step_result.req = req

            retry = Retry(merge(step_info["retry"], dft[step_info["ctx"]]["retry"]))
            until = Until(merge(step_info["until"], dft[step_info["ctx"]]["until"]))

            for i in range(until.attempts):
                for j in range(retry.attempts):
                    step_res = ctx[step_info["ctx"]].do(req)
                    sub_step_result.res = step_res
                    if retry.condition == "" or not check(retry.condition, case=case, step=sub_step_result, var=var, x=x):
                        break
                    time.sleep(retry.delay.total_seconds())
                else:
                    raise RetryError()
                if until.condition == "" or check(until.condition, case=case, step=sub_step_result, var=var, x=x):
                    break
                time.sleep(until.delay.total_seconds())
            else:
                raise UntilError()

            result = expect(step_res, json.loads(json.dumps(res)), case=case, step=sub_step_result, var=var, x=x)
            sub_step_result.add_expect_result(result)

            # ensure req can json serialize
            sub_step_result.req = json.loads(json.dumps(sub_step_result.req, default=lambda y: str(y)))
        except RetryError as e:
            sub_step_result.set_error("RetryError [{}]".format(retry))
        except UntilError as e:
            sub_step_result.set_error("UntilError [{}], ".format(until))
        except Exception as e:
            sub_step_result.set_error("Exception {}".format(traceback.format_exc()))
        sub_step_result.elapse = datetime.now() - sub_step_start
        return sub_step_result
