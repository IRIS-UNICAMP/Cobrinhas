import matplotlib.pyplot as plt

_range = 100000


def calc_eps(eps, s):
    new_eps = 1 / ((1 / eps) + s)
    return new_eps


def curve(_s):
    x = []
    y = []
    _eps = 1
    for i in range(_range):
        x.append(i)
        y.append(_eps)
        _eps = calc_eps(_eps, _s)

    return x, y


x1, y1 = curve(1)
x2, y2 = curve(0.1)
x3, y3 = curve(0.01)
x4, y4 = curve(0.001)
x5, y5 = curve(0.0001)

plt.plot(x1, y1, label='1')
plt.plot(x2, y2, label='0.1')
plt.plot(x3, y3, label='0.01')
plt.plot(x4, y4, label='0.001')
plt.plot(x5, y5, label='0.0001')


plt.ylim(0, 1)
plt.xlim(0, _range)

plt.xlabel('x - axis')
plt.ylabel('y - axis')

plt.legend()
plt.show()
