def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


for i in range(11):
    print(f"fib({i}) = {fibonacci(i)}")
