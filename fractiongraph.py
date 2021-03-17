# Consider a fraction fn = a/b. Then fn+1 = b/(a+b). What's this graph look like?
# ANS: duh... it's the ratio of fibonacci sequence, phi!

import numpy as np
from matplotlib import pyplot as plt

def frac_next(a, b):
    return b, a+b, b/(a+b)

N = 10
a, b = 1, 1

x = np.arange(1,N+1)
y = []
for i in range(N):
    if i < 10:
        print('{0}/{1}, '.format(a, b))
    a, b, _ = frac_next(a, b)
    y.append(frac_next(a, b)[2])

y = np.array(y)

phi = (1 + 5 ** 0.5) / 2
xphi = np.array([1/phi for i in range(N)])

fig = plt.subplots(figsize=[15,35])
plt.plot(x, y, c='black', ls='--', marker='x')
plt.plot(x, xphi, c='red', label='1/phi')
plt.title("fn=a/b, f(n+1)=b/(a+b) converges to 1/golden ratio")
plt.legend()
plt.show()
