import os
import io
import sys
import struct

def tell(file_object, endian = '<'):
	return file_object.tell()
def print_here(file_object, endian = '<'):
	print ("Here at:    {0:x}".format(tell(file_object)))
def print_hex(file_object, endian = '<'):
	print ("{0:x}".format(file_object))
def read_byte(file_object, endian = '<'):
	return struct.unpack(endian + 'B', file_object.read(1))[0]
def read_ushort(file_object, endian = '<'):
	return struct.unpack(endian + "H", file_object.read(2))[0]
def read_uint(file_object, endian = '<'):
	return struct.unpack(endian + 'I', file_object.read(4))[0]
def read_string(file_object):
	chars = []
	while True:
		c = read_byte(file_object)
		if c == 0x00:
			return "".join(chars)
		c = chr(c)
		chars.append(c)
def read_fixed_string(file_object, length):
	chars = []
	for x in range(0,length):
		chars.append(file_object.read(1).decode())
	return "".join(chars)
def read_fixed_byte_string(file_object, length, var1, var2):
	chars = []
	for x in range(0,length):
		chars.append(read_byte(file_object))
	if (var1 == 1):
		file_object.seek(-length, 1)
	if (var2 == 1):
		for x in range(0,length):
			print(('{0:02x}'.format(chars[x])), end = " ")
		print("")
def alignOffset(file_object, relOffset, alignment):
	if (relOffset % alignment) != 0:
		align = (alignment - (relOffset % alignment))
		file_object.seek(align, 1)

def writeBytesToFile(filePath, data):
	with open(filePath, 'wb') as file:
		file.write(data)


directory = r"C:\Users\Xavier\Downloads\JPKGReader-0.1.0\JPKGReader-0.1.0\JPKGReader\bin\Debug\net7.0\output\download"
allFiles = os.listdir(directory)
for fileName in allFiles:
	if fileName.split('.')[-1].lower() == 'jtex':
		filePath = os.path.join(directory, fileName)
		
		with open(filePath, 'rb') as f:
			magic = read_uint(f)
			fileSize = read_uint(f)

			f.seek(0x20)
			dds = f.read(fileSize - 0x20)

			outFile = filePath[:-13:] + fileName[:8:] + ".dds"
			writeBytesToFile(outFile,dds)