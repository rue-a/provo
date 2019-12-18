import inspect
import traceback

def getStack():
    '''
    returns the stack of methods-names, which where called until now
    https://docs.python.org/3/library/traceback.html
    '''
    # stack -> stack[0 -> n][0 -> m]
    # [0 -> n]: 0 - most high function/ module, n - current function
    # [0 -> m]: 0 - path, 1 - line where it's called, 2 - function name, 
    #   3 - line content
    stack = traceback.extract_stack()
    return [s[2] for s in stack]

def getMethodParametersAndValues(N=1):
    '''
    returns the parameters and corresponding values of the method
    N positions up in the stack. Default is one above since we do
    not want to return the params and vals of this method (N, 0)
    '''
    frame = inspect.currentframe()
    while N > 0:
        frame = frame.f_back
        N = N - 1
    args, _, _, values = inspect.getargvalues(frame)
    return ([(i, values[i]) for i in args])