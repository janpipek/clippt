function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

for (let i = 0; i <= 10; i++) {
    console.log(`fib(${i}) = ${fibonacci(i)}`);
}
