import random
import time

a = [[0] * 25][:] * 25
dic = {}
for i in range(25):
    for j in range(25):
        dic.update({"{}-{}".format(i, j): "{}-{}".format(i, j) * random.randint(0, 6)})

t = int(input("Time: "))
i = 0
time_1 = 0
time_2 = 0
while i < t:
    s_1 = time.time()
    for i in range(25):
        for j in range(25):
            print(a[i][j])

    e_1 = time.time()
    time_1 += (e_1 - s_1)
    s_2 = time.time()
    for i in range(25):
        for j in range(25):
            print(i + j)
    e_2 = time.time()
    time_2 += (e_2 - s_2)

print(time_1)
print(time_2)
