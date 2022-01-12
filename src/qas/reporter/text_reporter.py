#!/usr/bin/env python3


from src.qas.assertion.expect import TestResult, CaseResult, StepResult, ExpectResult


def report(test_result: TestResult):
    test_result.summary()
    print('\n'.join(test_summary(test_result)))


def test_summary(res: TestResult):
    lines = []
    if res.is_pass:
        lines.append("测试通过, 成功 {}".format(len(res.case_results)))
    else:
        lines.append("测试失败，成功 {}，失败 {}".format(
            sum(1 for i in res.case_results if i.is_pass),
            sum(1 for i in res.case_results if not i.is_pass),
        ))
    for case_result in res.case_results:
        lines.extend(["  " + i for i in case_summary(case_result)])
    return lines


def case_summary(res: CaseResult) -> list[str]:
    lines = []
    if res.is_pass:
        lines.append("case {} 通过".format(res.case))
    else:
        lines.append("case {} 失败".format(res.case))
    for step_result in res.step_results:
        lines.extend(["  " + i for i in step_summary(step_result)])
    return lines


def step_summary(res: StepResult) -> list[str]:
    lines = []
    if res.is_pass:
        lines.append("step {} 通过".format(res.step))
    else:
        lines.append("step {} 失败".format(res.step))
    for expect_result in res.expect_results:
        lines.append("  {}".format(expect_summary(expect_result)))
    return lines


def expect_summary(res: ExpectResult) -> str:
    if res.is_pass:
        return "node [{}] {}".format(res.node, res.message)
    else:
        return "node [{}] {}. val: {}, expect: {}".format(res.node, res.message, res.val, res.expect)
