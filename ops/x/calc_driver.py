class CalcDriver:
    def __init__(self, args):
        pass

    def default_step_name(self, req):
        return "echo"

    def do(self, req):
        return {"val": req["num1"] + req["num2"]}