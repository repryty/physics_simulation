from matplotlib.animation import FuncAnimation
import time
import math

import matplotlib.pyplot as plt

G = 9.8
DT = 60

THETA = 30 # 360 
STRING_LENGTH = 10 # m
M = 5 # kg

SPACE_LIMIT = 1.5 * STRING_LENGTH

fig, ax = plt.subplots()
ax.set_xlim(0, SPACE_LIMIT)
ax.set_ylim(0, SPACE_LIMIT)
point, = ax.plot([], [], 'ro', markersize=8)

x, y = [SPACE_LIMIT/2 + math.sin(THETA) * STRING_LENGTH, SPACE_LIMIT*3/4 + STRING_LENGTH * math.cos(THETA)]
v_right, v_up = 0, 0

def update(frame):
    v_up -= G / DT
    

    point.set_data([x], [y])

    return point



ani = FuncAnimation(fig, update, interval=33.33, blit=True)
plt.show()