import math

# Nhập bán kính của đường tròn từ người dùng
r = float(input("Nhập bán kính của đường tròn: "))

# Tính chu vi và diện tích
chu_vi = 2 * math.pi * r
dien_tich = math.pi * r**2

# Xuất kết quả
print(f"Chu vi của đường tròn là: {chu_vi}")
print(f"Diện tích của đường tròn là: {dien_tich}")
