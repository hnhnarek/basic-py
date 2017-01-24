

FUNCTION ex2()
  a = 3.14
  LET a = -777

  b = a + 1
  c = b - 2
  d = c * 3
  e = d / 4

  f = a > b AND c <= d
  g = NOT (a < b OR c >= d)
  
  PRINT e
END FUNCTION

CALL ex2

