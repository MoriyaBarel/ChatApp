import os.path
path = os.path.abspath('dog.jpg')
with open(path, 'rb') as f:

    data_s = f.read(2048)
    i = str(7)
    ib = i.encode()
    data = data_s + ib
    print(ib)
    print(data[:2048])
    print(int(data[2048:]))


