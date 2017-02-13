
FUNCTION ex4(n)
  WHILE n >= 0
    k = n * n + 3
    PRINT k
    n = n - 1
  END WHILE
END FUNCTION

FUNCTION Main()
  INPUT m
  CALL ex4 m
END FUNCTION
