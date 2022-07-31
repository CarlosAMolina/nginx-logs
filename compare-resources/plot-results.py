import matplotlib.pyplot as plt
import matplotlib as mpl

# https://matplotlib.org/stable/tutorials/introductory/customizing.html#runtime-rc-settings

mpl.rcParams["lines.linewidth"] = 2
mpl.rcParams["lines.linestyle"] = "--"
x = [0, 1, 2, 3, 4, 5]
y = [2, 3, 4, 8, 1, 2.3]
fig, ax = plt.subplots()
ax.plot(x, y)
fig.savefig("result.png")
