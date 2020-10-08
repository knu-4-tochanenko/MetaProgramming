# Check if three dots can create a triangle

(x1, y1) = float(input("x1:")), float(input("y1:"))
(x2, y2) = float(input("x2:")), float(input("y2:"))
(x3, y3) = float(input("x3:")), float(input("y3:"))

print('A[', x1, ';', y1, '], B[', x2, ';', y2, '], C[', x3, ';', y3, ']')

triangle_value = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)

if triangle_value > 0:
    print('Can create a triangle')
else:
    print('Can\'t create a triangle')
