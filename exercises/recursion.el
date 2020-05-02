#!/usr/bin/env emacs --script

(defun count-multiples (a b)
  "Count how many multiples of a are part of the factorization of b."
  ;; If a divides b, then the answer is 1 +
  (let ((rem (% b a)))
    (if (= rem 0) (1+ (count-multiples a (/ b a))) 0)))

(ert-deftest count-multiples ()
  (should (equal (count-multiples 2 6) 1))
  (should (equal (count-multiples 2 12) 2))
  (should (equal (count-multiples 3 11664) 6)))


(defun maxval (x)
  (if (cdr x)
      (max (car x) (maxval (cdr x)))
    (car x)))

(ert-deftest maxval ()
  (should (equal (maxval '(1 9 -3 7 13 2 3)) 13)))


(defun flatten (x)
  (if (listp x)
      (let ((flattened-car (flatten (car x))))
        (if (cdr x)
            (append flattened-car (flatten (cdr x)))
          flattened-car))
    (list x)))

(ert-deftest flatten ()
  (should (equal (flatten '(1 (2 (3 4) 5) 6))
                 '(1 2 3 4 5 6))))
