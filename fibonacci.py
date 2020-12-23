# quick fibonacci generator

def fibonacci(n):
    '''return nth fibonacci number'''
    return 0 if n<1 else 1 if n==1 else fibonacci(n-1)+fibonacci(n-2)

# print first N fib numbers
N = 10
for n in range(N):
    print(fibonacci(n), end='')
    if n < (N-1):
        print(', ', end='')
    else:
        print()
