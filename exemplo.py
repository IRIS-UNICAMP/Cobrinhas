conjunto = set()

for x in range(0, 620, 20):
    for y in range(0, 620, 20):
        quadrado = (x, y)
        conjunto.add(quadrado)

nova_comida = random.choices(conjunto)

"""
####

0 -> 600, 20 em 20 (x)
0 -> 600, 20 em 20, (y)
conjunto = set()

excluir valores que façam parte da cobra

for i in range(0, 620, 20):
    print(i)


####
"""

# 32
