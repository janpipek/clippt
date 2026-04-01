local function fibonacci(n)
    if n <= 1 then return n end
    return fibonacci(n - 1) + fibonacci(n - 2)
end

for i = 0, 10 do
    print(string.format("fib(%d) = %d", i, fibonacci(i)))
end
