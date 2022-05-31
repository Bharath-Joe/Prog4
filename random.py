def main():
    f = open("random.txt", "rb+")
    for i in range(10240):
        f.write(b"#")
    f.close()
    callRwrite()

def callRwrite():
    # f = open("random.txt", "rb")
    # contents = f.read()
    # f.close()

    f = open("random.txt", "rb+")
    # f.write(contents)
    f.seek(10000)
    f.write(b"F")


if __name__ == '__main__':
    main()
    