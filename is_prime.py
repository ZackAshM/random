# quick attempt for a prime checker

# check if prime function
def is_prime(n):
    # obvious condition
    if n<=1:
        return False

    # any prime divisors?
    for d in range(2, int(n**0.5)+1):
        if is_prime(d):
            if not(n%d):
                return False

    # prime
    return True
