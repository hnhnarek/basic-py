
FUNCTION Pr(x, n)
  FOR i = 1 TO n
    PRINT x[i]
  END FOR
END FUNCTION

FUNCTION Main()
  DIM w[5]

  FOR i = 1 TO 5
    w[i] = i^2
  END FOR

  CALL Pr w, 5
END FUNCTION
