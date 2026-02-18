(define (fibonacci n)
  (cond ((= n 0) 0)
        ((= n 1) 1)
        (else (+ (fibonacci (- n 1))
                 (fibonacci (- n 2))))))

(do ((i 0 (+ i 1)))
    ((> i 10))
  (display (string-append "fib(" (number->string i) ") = "
                          (number->string (fibonacci i))))
  (newline))
