# import os.path
# path = os.path.abspath('dog.jpg')
# with open(path, 'rb') as f:
#
#     data_s = f.read(2048)
#     i = str(7)
#     ib = i.encode()
#     data = data_s + ib
#     print(ib)
#     print(data[:2048])
#     print(int(data[2048:]))

def split_packets(packets: list) -> set:
    ans = []
    for packet in packets:
        if len(packet) > 2:
            i = 0
            while i < int((len(packet))/2)+1:
                ans.append(packet[i:i+2])
                i += 2
        else:
            ans.append(packet)
    return set(ans)


if __name__ == '__main__':
    ls = split_packets(['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '1300', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '1300', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13'])
    print(ls)


