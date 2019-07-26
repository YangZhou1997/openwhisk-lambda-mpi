import glob
import matplotlib
matplotlib.use('Agg')

from pylab import *
import pylab
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
    'figure.figsize': [12, 6.18]
}
rcParams.update(params)


def load(filePath):
    x = np.zeros(8)
    latencies = np.zeros((8, 10))
    xcount = 0
    ycount = 0
    for line in open(filePath):
        if line.count('.') == 0:
            sendnum = int(line.rstrip("\n"))
            x[xcount] = sendnum
            xcount += 1
            ycount = 0
        else:
            latency = float(line.rstrip("\n"))
            latencies[xcount - 1][ycount] = latency
            ycount += 1
    return x, latencies


def perc(data):    
    median = np.zeros(data.shape[0])
    perc_5 = np.zeros(data.shape[0])
    perc_95 = np.zeros(data.shape[0])
    for i in range(0, len(median)):
        temp = np.trim_zeros(data[i, :])
        median[i] = np.median(temp)
        perc_5[i] = np.percentile(temp, 5)
        perc_95[i] = np.percentile(temp, 95)
    return median, perc_5, perc_95


x, data_msg = load('../data_trans/msg_data_trans_sendnum.txt')
# print data_msg
x, data_redis = load('../data_trans/redis_data_trans_sendnum.txt')
# print data_redis

_x = []
for i in x:
    if i < 1024:
        _x.append(str(i) + 'B')
    elif i < 1024 * 1024:
        _x.append(str(i // 1024) + 'KB')
    else:
        _x.append(str(i // (1024 * 1024)) + 'MB')
# print _x


med_msg, perc_5_msg, perc_95_msg = perc(data_msg)
# print med_msg
med_redis, perc_5_redis, perc_95_redis = perc(data_redis)
# print med_redis

print (med_redis - med_msg) / med_msg

fig = figure() # no frame
ax = fig.add_subplot(111)

# now all plot function should be applied to ax
ax.fill_between(x, perc_5_msg, perc_95_msg, alpha=0.25, linewidth=0, color=colors[0]) 
ax.fill_between(x, perc_5_redis, perc_95_redis, alpha=0.25, linewidth=0, color=colors[1])
ax.plot(x, med_msg, linewidth=2, color=colors[0])
ax.plot(x, med_redis, linewidth=2, linestyle='--', color=colors[1])

pylab.xlabel('# 64B-messages')
pylab.ylabel('Transferal time (Seconds)')

# change xlim to set_xlim
# ax.set_xlim(-5, 400)
# ax.set_ylim(-5000, 300)

#change xticks to set_xticks
ax.set_xticks(np.arange(0, 128 + 1, 16))

labelX = []
for i in np.arange(0, 128 + 1, 16):
    labelX.append(str(2 * i))
ax.set_yscale('log')
ax.set_xticklabels(labelX)

legend = ax.legend(["Messaging", "Redis"], loc=2);
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')

fig.savefig('sendnum.pdf')