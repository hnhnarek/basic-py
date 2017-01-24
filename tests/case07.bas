
' asdad
FUNCTION ex6(a)
  IF a = 1 THEN
    ' first
    PRINT a
  ELSEIF a = 2 THEN
    ' second
    ' third as
    PRINT a * 2
  ELSEIF a = 3 THEN
    PRINT a * 3
  ELSEIF a = 4 THEN
    PRINT a / 2
  ELSE
    PRINT a * a
  END IF
END FUNCTION

CALL ex6 1
CALL ex6 2
CALL ex6 3
CALL ex6 4
CALL ex6 8
