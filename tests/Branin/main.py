import numpy as np

def branin_function(x1, x2):
    # Parameters of the function
    PI = 3.14159265359
    a = 1
    b = 5.1 / (4 * pow(PI, 2))
    c = 5 / PI
    r = 6
    s = 10
    t = 1 / (8 * PI)

    f = a*(x2 - b*x1**2 + c*x1 - r)**2 + s*(1-t)*np.cos(x1) + s

    return f

x1 = __Parameters, x1, -__
x2 = __Parameters, x2, -__

print(branin_function(x1,x2))
