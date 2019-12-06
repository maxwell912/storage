import matplotlib.pyplot as plt


def lineplot(x_data, y_data):
    _, ax = plt.subplots()
    ax.plot(x_data, y_data)
    plt.show()


if __name__ == '__main__':
    import time
    from progr_files.Server import Server
    from progr_files.Client import Client
    import threading

    server = Server('127.0.0.5', 8000)
    th = threading.Thread(target=server.start)
    th.daemon = True
    th.start()
    client = Client([('127.0.0.5', 8000)])
    # client = Storage()
    x_data = list()
    y_data = list()
    for i in range(10000):
        print(i)
        t = time.time()
        client.add(i, i)
        s = time.time() - t
        x_data.append(i)
        y_data.append(s)
    lineplot(x_data, y_data)
