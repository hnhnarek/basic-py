
FUNCTION ex3(n)
  FOR i = n + 3 TO 1 STEP -2
    PRINT i
    'PRINT i * 2
  END FOR
END FUNCTION

FUNCTION Main()
  CALL ex3 5
END FUNCTION
