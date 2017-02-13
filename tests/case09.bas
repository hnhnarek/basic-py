
'
' Quadratic equation solved
'
FUNCTION Quadratic(a, b, c)
  IF a = 0 THEN
    IF b = 0 THEN
      IF c = 0 THEN
        PRINT "Too many roots."
      ELSE
        PRINT "No one root."
      END IF
    ELSE
      PRINT "One root:"
      PRINT -c / b
    END IF
  ELSE
    d = b^2 - 4*a*c
    IF d < 0 THEN
      PRINT "No real roots."
    ELSE
      PRINT "Two roots:"
      PRINT (-b + SQR(d)) / (2 * a)
      PRINT (-b - SQR(d)) / (2 * a)
    END IF
  END IF
END FUNCTION

'
'
'
FUNCTION Main()
  CALL Quadratic 0, 0, 0
  CALL Quadratic 0, 0, 3
  CALL Quadratic 0, 2, 3
  CALL Quadratic -1, 2, 3
END FUNCTION

