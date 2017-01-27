
'
'
'
FUNCTION BubbleSort(x)
  n = LEN(x)
  FOR i = 1 TO n - 1
    FOR j = i TO n
      IF x[i] > x[j] THEN
        temp = x[i]
        x[i] = x[j]
        x[j] = temp
      END IF
    END FOR
  END FOR

  BubbleSort = x
END FUNCTION

'
'
'
FUNCTION Main()
  DIM w[5]

  w[1] = 6
  w[2] = 2
  w[3] = 9
  w[4] = 4
  w[5] = 8

  w0 = BubbleSort(w)
  PRINT w0
END FUNCTION


