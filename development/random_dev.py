#script to demonstrate multiple figures on subplot problem

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

x = np.linspace(0, 1, 100)
y = np.sin(2*np.pi*x)

fig, ax = plt.subplots(nrows=100)

for axis in ax:
    axis.plot(x, y)
    axis.set(yticks=[],
             xticks=[])
    sns.despine(ax=axis)

fig.text(0.5, 0.05, "x title", ha='center')
fig.text(0.05, 0.5, "y title", va='center', rotation='vertical')
fig.text(0.5, 0.9, "panel title", ha='center')

fig.subplots_adjust(hspace=0)

plt.show()

import matplotlib.pyplot as plt

fig1, ax = plt.subplots()
ax.plot(range(10))
ax.remove()

fig2 = plt.figure()
ax.figure=fig2
fig2.axes.append(ax)
fig2.add_axes(ax)

dummy = fig2.add_subplot(111)
ax.set_position(dummy.get_position())
dummy.remove()
plt.close(fig1)

plt.show()

import matplotlib.gridspec as gridspec

fig = plt.figure()
gs0 = fig.add_gridspec(3, 1)
ax1 = fig.add_subplot(gs0[0])
ax2 = fig.add_subplot(gs0[1])
gssub = gs0[2].subgridspec(1, 3)
for i in range(3):
    fig.add_subplot(gssub[0, i])
    
    