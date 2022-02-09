class CalcDriver:
    def __init__(self, args):
        pass

    def default_step_name(self, req):
        return "calc"

    def do(self, req):
        return {"val": req["num1"] + req["num2"]}