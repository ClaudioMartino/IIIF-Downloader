class Test:
    def __init__(self, ref):
        self.ref = ref
        self.result = None

    def check_ref(self):
        if (self.result != self.ref):
            raise Exception(
                str(type(self)) + " Error! Result: " + str(self.result) +
                " (" + str(type(self.result)) + "). Ref.: " + str(self.ref) +
                " (" + str(type(self.ref)) + ").")
