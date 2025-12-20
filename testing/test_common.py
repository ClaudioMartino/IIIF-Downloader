class Test:
    def __init__(self, ref):
        self.ref = ref
        self.result = None

    def run_and_check_ref(self, *args):
        self.run(*args)
        self.check_ref()

    def check_ref(self):
        if (self.result != self.ref):
            raise Exception(
                str(type(self)) + " Error! Result: " + str(self.result) +
                " (" + str(type(self.result)) + "). Ref.: " + str(self.ref) +
                " (" + str(type(self.ref)) + ").")

    def run_and_check_exception(self, *args):
        try:
            self.run(*args)
        except Exception:
            return
        raise Exception("Exception not raised, when it should be.")
