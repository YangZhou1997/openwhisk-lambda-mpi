import struct

f = open("test.dat", 'wb')
total_size = 0x01234567
print(hex(total_size))
f.write(struct.pack(">I", total_size))
f.close()


f = open("test.dat", 'rb')
total_size = f.read(4)
print(hex(struct.unpack("<I", total_size)[0]))
f.close()

