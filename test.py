import os

if __name__ == '__main__':
    str = "##name.jpg#test1"


    def get_filename_and_filetype(msg_str: str):
        actual_msg = msg_str[2:]
        mstr = actual_msg.split('#')
        filenameandfiletype = mstr[0]
        save = mstr[1]
        print(type(filenameandfiletype))


        file = filenameandfiletype.split('.')
        filename = file[0]
        file_type = file[1]

        return filename,file_type, save

    recv_msg = " ##download#b'31'#jpg'#47185"
    actual = recv_msg[12:]
    save_as, file_type, file_size = actual.split('#')
    print("save: ", save_as)
    save = save_as[2:-1]
    print(len(save))
    print(save)
    print(type(save_as))








