from qas.driver import Driver


class EchoDriver(Driver):
    def __init__(self, args):
        pass

    def default_step_name(self, req):
        return "echo"

    def do(self, req):
        return req
