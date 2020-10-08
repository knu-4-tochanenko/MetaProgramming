# Find roots of square equation by it's parameters
import math

a = int(input("Enter A:"))
b = int(input("Enter B:"))
c = int(input("Enter C:"))

print("Calculating roots for equation:")
print(a, 'x^2 + (', b, ') * x + (', c, ')')

# Calculate discriminant
d = b**2 - 4 * a * c

if d < 0:
    print("The equation does not have real solutions")
elif d == 0:
    print(-b / (2 * a))
else:
    print(-b + math.sqrt(d) / (2 * a), -b - math.sqrt(d) / (2 * a))
