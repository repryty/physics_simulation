from matplotlib.animation import FuncAnimation
import time

import matplotlib.pyplot as plt

g = 9.8
dt = 30

y0=100.0 

y = y0
v = 0

font_dict={'fontname': 'Noto Sans KR', 'fontweight': 'bold'}

fig, ax = plt.subplots()
ax.set_xlim(0, 1)
ax.set_ylim(0, y0+1)
point, = ax.plot([], [], 'ro', markersize=8)
ax.set_title(f"시작 높이 {y}", fontdict=font_dict)
text = ax.text(0.1, 0.8, "", transform=ax.transAxes, fontsize=12, color="black", fontdict=font_dict)

a=0
data_y=[]
data_v=[]
b=0

def update(frame):
    global y, v, a, b, data_y, data_v
    if b>100:
        v += g / dt
        y = max([y - (v / dt), 0])
        point.set_data([0.5], [y])
        text.set_text(f"현재 위치: {y:.3f}\n현재 속도: {v:.3f}\n현재 시간: {len(data_v)/30:.3f}초")
        
        if a==0:
            data_y.append(y)
            data_v.append(v)

        if y <= 0 and a==0:
            a+=1
        elif y<=0 and a!=0:
            a+=1
            ani.event_source.stop()
            return point,text
    else:
        b+=1
    return point, text

ani = FuncAnimation(fig, update, interval=33.33, blit=True)
plt.show()

plt.clf()

data_v.pop()
data_y.pop()

plt.plot(data_y, label="위치")
plt.plot(data_v, label="속도")
plt.legend(prop={'family':'Noto Sans KR'})

plt.show()