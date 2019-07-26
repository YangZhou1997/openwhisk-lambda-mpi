import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

import brewer2mpl

 # brewer2mpl.get_map args: set name  set type  number of colors
bmap = brewer2mpl.get_map('Set2', 'qualitative', 7)
colors = bmap.mpl_colors
 
params = {
    'axes.labelsize': 18,
    'font.size': 18,
    'legend.fontsize': 18,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'text.usetex': False,
    'figure.figsize': [20, 8],
    'legend.loc': 'best'
}
rcParams.update(params)


def load(filePath):
    x = np.zeros(8, int)
    systime = np.zeros((3, 8))
    usertime = np.zeros((3, 8))
    inittime = np.zeros((3, 8))

    avgsystime = np.zeros((10, 8))
    avgusertime = np.zeros((10, 8))
    avginittime = np.zeros((10, 8))

    f = open(filePath, 'r')
    for j in range(10):
        for i in range(8):
            f.readline()
            sysline = f.readline().rstrip("\n")
            sysarray = map(float, sysline.strip('[').strip(']').split(','))
            avgsystime[j][i] = np.average(sysarray)
            # systime[1][i] = np.percentile(sysarray, 5)
            # systime[2][i] = np.percentile(sysarray, 95)

            f.readline()
            userline = f.readline().rstrip("\n")
            userarray = map(float, userline.strip('[').strip(']').split(','))
            avgusertime[j][i] = np.average(userarray)
            # usertime[1][i] = np.percentile(userarray, 5)
            # usertime[2][i] = np.percentile(userarray, 95)

            f.readline()
            initline = f.readline().rstrip("\n")
            initarray = map(float, initline.strip('[').strip(']').split(','))
            avginittime[j][i] = np.average(initarray)
            # inittime[1][i] = np.percentile(initarraym 5)
            # inittime[2][i] = np.percentile(initarray, 95)

            f.readline()
            x[i] = int(1 << i)
    # print avgsystime
    # print avgusertime
    # print avginittime

    for i in range(8):
        systime[0][i] = np.median(avgsystime[:, i])
        systime[1][i] = np.percentile(avgsystime[:, i], 5)
        systime[2][i] = np.percentile(avgsystime[:, i], 95)

        usertime[0][i] = np.median(avgusertime[:, i])
        usertime[1][i] = np.percentile(avgusertime[:, i], 5)
        usertime[2][i] = np.percentile(avgusertime[:, i], 95)
        
        inittime[0][i] = np.median(avginittime[:, i])
        inittime[1][i] = np.percentile(avginittime[:, i], 5)
        inittime[2][i] = np.percentile(avginittime[:, i], 95)
        
    return x, systime/1000, usertime/1000, inittime/1000

x, msg_systime, msg_usertime, msg_inittime = load('../ow_overhead/msg_ow_results.txt')
# print x
# print msg_systime
# print msg_usertime
# print msg_inittime
x, ori_systime, ori_usertime, ori_inittime = load('../ow_overhead/ori_ow_results.txt')
# print x
# print ori_systime
# print ori_usertime
# print ori_inittime

a = (msg_systime - ori_systime) / ori_systime
print np.min(a[0, :]), np.max(a[0, :])

a = (msg_usertime - ori_usertime) / ori_usertime
print np.min(a[0, :]), np.max(a[0, :])

a = (msg_systime[0, :] + msg_usertime[0, :] + msg_inittime[0, :] - (ori_systime[0, :] + ori_usertime[0, :] + ori_inittime[0, :])) / (ori_systime[0, :] + ori_usertime[0, :] + ori_inittime[0, :])
print np.min(a), np.max(a)

systime = np.zeros((3, 16))
usertime = np.zeros((3, 16))
inittime = np.zeros((3, 16))

for i in range(16):
    if i % 2 == 1:
        systime[:, i] = msg_systime[:, i//2]
        usertime[:, i] = msg_usertime[:, i//2]
        inittime[:, i] = msg_inittime[:, i//2]
    else:
        systime[:, i] = ori_systime[:, i//2]
        usertime[:, i] = ori_usertime[:, i//2]
        inittime[:, i] = ori_inittime[:, i//2]

yerr_systime = np.zeros((2, 16))
yerr_systime[0, :] = systime[0, :] - systime[1, :]
yerr_systime[1, :] = systime[2, :] - systime[0, :]

yerr_usertime = np.zeros((2, 16))
yerr_usertime[0, :] = usertime[0, :] - usertime[1, :]
yerr_usertime[1, :] = usertime[2, :] - usertime[0, :]

yerr_inittime = np.zeros((2, 16))
yerr_inittime[0, :] = inittime[0, :] - inittime[1, :]
yerr_inittime[1, :] = inittime[2, :] - inittime[0, :]


N = 16

ind = np.arange(N) * 10 + 10    # the x locations for the groups
for i in range(len(ind)):
    if i % 2 == 0:
        ind[i] += 2
    else:
        ind[i] -= 2

# print ind
width = 3.5       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, systime[0, :], width, yerr=yerr_systime, color=colors[0], ecolor=colors[0], align="center")
p2 = plt.bar(ind, inittime[0, :], width, bottom=systime[0, :], yerr=yerr_inittime, color=colors[2], ecolor=colors[2], align="center")
p3 = plt.bar(ind, usertime[0, :], width, bottom=systime[0, :]+inittime[0, :], yerr=yerr_usertime, color=colors[1], ecolor=colors[1], align="center")

plt.ylabel('Time (Seconds)')

# plt.title('Scores by group and gender')

plt.xlim(0, 170)

plt.xticks(ind, ('OW-1', 'Pik-1', 'OW-2', 'Pik-2', 'OW-4', 'Pik-4', 'OW-8', 'Pik-8', 'OW-16', 'Pik-16', 'OW-32', 'Pik-32', 'OW-64', 'Pik-64', 'OW-128', 'Pik-128', ))
# plt.yticks(np.arange(0, 81, 10))
plt.xticks(rotation = 35, ha="right", rotation_mode="anchor")
plt.legend((p3[0], p2[0], p1[0]), ('Execution time', 'Initialization time', 'Wait time'))

plt.savefig('overhead.pdf')