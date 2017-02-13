
FUNCTION fact(n)
  IF n = 1 THEN
    fact = 1
  ELSE
    fact = n * fact(n - 1)
  END IF
END FUNCTION

FUNCTION Main()
  PRINT SQR(fact(6))
END FUNCTION
