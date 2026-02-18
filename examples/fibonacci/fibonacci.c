#include <stdio.h>

long fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    for (int i = 0; i <= 10; i++) {
        printf("fib(%d) = %ld\n", i, fibonacci(i));
    }
    return 0;
}
