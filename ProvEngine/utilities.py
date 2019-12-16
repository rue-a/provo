import inspect
import traceback

def getStack():
    # stack -> stack[0 -> n][0 -> m]
    # [0 -> n]: 0 - most high function/ module, n - current function
    # [0 -> m]: 0 - path, 1 - line, 2 - function name, 3 - line content
    stack = traceback.extract_stack()
    return [s[2] for s in stack[1:-2]]

def getFunctionParametersAndValues():
    frame = inspect.currentframe().f_back.f_back
    args, _, _, values = inspect.getargvalues(frame)
    return ([(i, values[i]) for i in args])