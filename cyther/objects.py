

class SimpleCommand:
    def __init__(self):
        self.runtime_names = []
        self.include_names = []
        self.cython_name = None
        self.python_name = None
        self.c_name = None
        self.o_name = None
        self.dll_name = None

    def getCythonFileName(self):
        return self.cython_name

    def setCythonFileName(self, obj):
        self.cython_name = obj

    def getPythonFileName(self):
        return self.python_name

    def setPythonFileName(self, obj):
        self.python_name = obj

    def getCName(self):
        return self.c_name

    def setCName(self, obj):
        self.c_name = obj

    def getOName(self):
        return self.o_name

    def setOName(self, obj):
        self.o_name = obj

    def getDLLName(self):
        return self.dll_name

    def setDLLName(self, obj):
        self.dll_name = obj

    def getRuntimeNames(self):
        return self.runtime_names

    def setRuntimeNames(self, obj):
        self.runtime_names = obj

    def getIncludeNames(self):
        return self.include_names

    def setIncludeNames(self, obj):
        self.include_names = obj
