import io
import sys
import math
import struct
import uuid
import os
import gc


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
def read_short(file_object, endian = '<'):
	return struct.unpack(endian + 'h', file_object.read(2))[0]
def read_uint(file_object, endian = '<'):
	return struct.unpack(endian + 'I', file_object.read(4))[0]
def read_int(file_object, endian = '<'):
	return struct.unpack(endian + 'i', file_object.read(4))[0]
def read_longlong(file_object, endian = '<'):
	return struct.unpack(endian + 'q', file_object.read(8))[0]
def read_ulonglong(file_object, endian = '<'):
	return struct.unpack(endian + 'Q', file_object.read(8))[0]
def read_half(file_object, endian = '<'):
	return struct.unpack(endian + 'e', file_object.read(2))[0]
def read_float(file_object, endian = '<'):
	return struct.unpack(endian + 'f', file_object.read(4))[0]
def read_vec2(file_object, endian = '<'):
	return struct.unpack(endian + 'ff', file_object.read(8))
def read_vec3(file_object, endian = '<'):
	return struct.unpack(endian + 'fff', file_object.read(12))
def read_vec4(file_object, endian = '<'):
	return struct.unpack(endian + 'ffff', file_object.read(16))
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
	x = 0
	while x < length:
		try:
			chars.append(file_object.read(1).decode('utf-8'))
			x += 1
		except UnicodeDecodeError:
			file_object.seek(-1, 1)
			chars.append(file_object.read(2).decode('shift-jis'))
			x += 2
	return "".join(chars).rstrip('\x00')
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
def reverse_string(string):
	return string[::-1]
def get_key(val, dict):
	for key, value in dict.items():
		if val == value:
			return key
	return 0
def get_string(file_object, offset):
	backJump = tell(file_object)
	file_object.seek(offset)
	string = read_string(file_object)
	file_object.seek(backJump)
	return string

class _fileTable(object):
	def __init__(self, file_object):
		self.fileName = read_fixed_string(file_object, 0x60)
		self.fileOffset = read_uint(file_object)
		self.fileSize = read_uint(file_object)
		
		

filePath = r"D:\models\ripped\dbz nds\origins\root\character\DBMODEL.bin"
f = open(filePath, "rb")

LINK = read_uint(f)
null = read_uint(f)
fileCount = read_uint(f)
fileTableOffset = read_uint(f)
null = read_uint(f)
fileSize = read_uint(f)
unk = read_uint(f)
null = read_uint(f)

f.seek(fileTableOffset)
fileTableList = [_fileTable(f) for x in range(fileCount)]

for fileTable in fileTableList:
	outPath = (os.path.dirname(filePath) + "/" + os.path.basename(filePath).split(".")[0] + "/" + fileTable.fileName).replace("\\", "/")
	print(outPath)

	# print(fileTable.fileName)

	f.seek(fileTable.fileOffset)
	file = f.read(fileTable.fileSize)

	# Ensure the directory exists
	os.makedirs(os.path.dirname(outPath.replace("/", "//")), exist_ok=True)

	# Open the file in binary write mode and write the data
	with open(outPath, 'wb') as binary_file:
		binary_file.write(file)





print("Last read @ {0:x}".format(tell(f)))
f.close()