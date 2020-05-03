#!/usr/bin/env emacs --script
(require 'seq)

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
      (if (cdr x)
          (append (flatten (car x)) (flatten (cdr x)))
        (flatten (car x)))
    (list x)))

(ert-deftest flatten ()
  (should (equal (flatten '(1 (2 (3 4) 5) 6))
                 '(1 2 3 4 5 6))))


(defun count-occurences (a x)
  (if (listp x)
      (if (cdr x)
          (+ (count-occurences a (car x)) (count-occurences a (cdr x)))
        (count-occurences a (car x)))
    (if (eq x a) 1 0)))


(ert-deftest count-occurences ()
  (should (equal (count-occurences 2 '(1 (4 (5 2) 2) (8 (2 9)))) 3)))


(defun vector-to-list (x)
  (if (vectorp x)
      (if (> (length x) 0)
          (cons (vector-to-list (aref x 0))
                (vector-to-list (seq-drop x 1))))
    x))

(ert-deftest vector-to-list ()
  (should (equal (vector-to-list [1 [2 3]])
                 '(1 (2 3))))
  (should (equal (vector-to-list [1 [4 [5 2] 2] [8 [2 9]]])
                 '(1 (4 (5 2) 2) (8 (2 9))))))
