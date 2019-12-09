import time

import matplotlib.pyplot as plt


def lineplot(x_data, y_data):
    _, ax = plt.subplots()
    ax.plot(x_data, y_data)
    plt.show()


def f_plot(*args, **kwargs):
    xlist = []
    ylist = []
    for i, arg in enumerate(args):
        if i % 2 == 0:
            xlist.append(arg)
        else:
            ylist.append(arg)

    colors = kwargs.pop('colors', 'k')
    linewidth = kwargs.pop('linewidth', 1.)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    i = 0
    for x, y, color in zip(xlist, ylist, colors):
        i += 1
        ax.plot(x, y, color=color, linewidth=linewidth, label=str(i))

    ax.grid(True)
    ax.legend()
    plt.show()


def time_add(client):
    i = 0
    while True:
        t = time.time()
        client.add(i, i)
        yield time.time() - t
        i += 1


def time_get(client):
    i = 0
    while True:
        t = time.time()
        client.get(i)
        yield time.time() - t
        i += 1


def get_data():
    from progr_files.Server import Server
    from progr_files.Client import Client

    server = Server(('127.0.0.5', 8000))
    server.start()
    client = Client([('127.0.0.5', 8000)])
    n = 1000
    a = 10
    p = n // a
    x_data = list(range(0, n, a))
    y_data = list()
    y_data2 = list()
    t_a = time_add(client)
    t_g = time_get(client)
    for i in range(p):
        print(i)
        s_a = 0
        s_g = 0
        for j in range(a):
            s_a += next(t_a)
            s_g += next(t_g)
        y_data.append(s_a / a)
        y_data2.append(s_g / a)
    server.stop()
    return x_data, y_data, y_data2


if __name__ == '__main__':
    data = get_data()
    f_plot(data[0], data[1], data[0], data[2],
           colors=['red', 'blue'], linewidth=2.)
