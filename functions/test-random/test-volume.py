def main(args):
    f = open("/addrMap/test-file.txt", 'r')
    test_line = f.readline()
    f.close()
    f = open("/addrMap/test-file.txt", 'a')
    f.write("sending data from container to host")
    f.close()
    return {"result": test_line}

