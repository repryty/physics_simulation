import math
import random

def colaz(n):
    data1, data2=[], []
    while n > 1:
        if n%2==0:
            n/=2
        else:
            n=3*n+1
        data1.append(math.log(n))
        data2.append(n)
    return data1, data2

import matplotlib.pyplot as plt


data = colaz(random.randint(1,999999999999999))
plt.plot(data[1])
plt.show()

plt.plot(data[0])
plt.show()