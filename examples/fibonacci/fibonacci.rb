def fibonacci(n)
  return n if n <= 1
  fibonacci(n - 1) + fibonacci(n - 2)
end

(0..10).each { |i| puts "fib(#{i}) = #{fibonacci(i)}" }
