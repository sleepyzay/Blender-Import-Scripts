import io
import sys
import math
import struct
import os
import numpy
import tkinter as tk
from tkinter import filedialog

def open_file():
	root = tk.Tk()
	root.withdraw()  # Hide the root window
	file_path = filedialog.askopenfilename(
		filetypes=[("TPL files", "*.tpl")]  # Restrict to .tpl files
	)
	return file_path

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
	for x in range(0,length):
		chars.append(file_object.read(1).decode())
	return "".join(chars)
def read_fixed_byte_string(file_object, length, var1, var2):
	chars = []
	for x in range(length):
		chars.append(read_byte(file_object))

	if var1 == 1:
		file_object.seek(-length, 1)

	# Create the formatted string
	result_string = " ".join(['{0:02x}'.format(char) for char in chars])

	# Print the string if var2 == 1
	if var2 == 1:
		print(result_string)

	# Return the string regardless
	return result_string
def reverse_string(string):
	return string[::-1]
def get_key(val, dict):
	for key, value in dict.items():
		if val == value:
			return key
	return 0
def getString(file_object, stringOffset):
	backJump = tell(file_object)
	file_object.seek(stringOffset)
	s = read_string(file_object)
	file_object.seek(backJump)
	return s
def alignOffset(file_object, relOffset, alignment):
	if (relOffset % alignment) != 0:
		align = (alignment - (relOffset % alignment))
		file_object.seek(align, 1)
def write_float(f,float_value):
	binary_data = struct.pack('f', float_value)
	f.write(binary_data)
def getIndex(f, offset):
	returnOffset = tell(f)
	index = 0
	if offset > 0:
		f.seek(offset)
		index = read_uint(f)
		f.seek(returnOffset)
	return(index)
def bits_to_string(bit_list, n=0, reverse_bytes=False):
	# Split the bit_list into chunks of 8 (bytes)
	byte_chunks = [bit_list[i:i+8] for i in range(0, len(bit_list), 8)]
	
	if reverse_bytes:
		# Reverse each chunk (byte) if reverse_bytes is True
		byte_chunks = [byte[::-1] for byte in byte_chunks]
	
	# Join the bytes back into a string
	bit_str = ''.join([''.join(map(str, byte)) for byte in byte_chunks])
	
	# If n > 0, add spaces after every n characters
	if n > 0:
		return ' '.join([bit_str[i:i+n] for i in range(0, len(bit_str), n)])
	else:
		return bit_str
def readBits(f, bitCount, reverse_bits_per_byte=False, reverse_bit_order=False):
	# Read the necessary bytes from the file
	bytes_data = f.read(math.ceil(bitCount / 8))
	
	# Extract bits from each byte
	bits = []
	for byte in bytes_data:
		# Extract bits in normal order (MSB to LSB)
		byte_bits = [(byte >> bit) & 1 for bit in range(8)]
		
		# Reverse bits within each byte if specified
		if reverse_bits_per_byte:
			byte_bits = byte_bits[::-1]
		
		bits.extend(byte_bits)
	
	# Limit the list to the required bit count
	bits = bits[:bitCount]
	
	# Reverse the entire bit order if specified
	if reverse_bit_order:
		bits = bits[::-1]
	
	return bits

def findNum(f, searchNum, searchLimit = 0x10000):
	initialOffset = tell(f)
	fileSize = os.stat(filePath).st_size
	while (tell(f) < initialOffset + searchLimit) or (tell(f) < fileSize):
		num = f.read(4)
		value = struct.unpack('<I', num)[0]
		if value != searchNum:
			f.seek(-0x03, 1)
		else:
			numOffset = tell(f) - 0x04
			f.seek(initialOffset)
			return (numOffset)
	f.seek(initialOffset)

		

		

class _nodeData():
	def __init__(self, f):
		self.nodeId = read_uint(f)
		self.unk = read_uint(f)				# 0x01
		self.unk2 = read_byte(f)			# 0x01
		self.unk3 = read_byte(f)			# 0x01
		self.unk4 = read_byte(f)			# 0x00
		self.unk5 = read_byte(f)			# 0x01
		self.unk6 = read_uint(f)			# null?

class _meshData():
	# Describes which buffers the mesh reads from and the base offsets whithin each buffer to be read from
	def __init__(self, f):
		# read_fixed_byte_string(f, 0x08, 1, 1)

		self.bufferId = read_uint(f)
		self.subBufferOffset = read_uint(f)
class _subMeshData():
	def __init__(self, f):
		read_fixed_byte_string(f, 0x10, 1, 0)
		self.vertexIndex = read_ushort(f)
		self.vertexCount = read_ushort(f)
		self.faceIndex = read_ushort(f)
		self.faceCount = read_ushort(f)
		self.nodeId = read_ushort(f)					# 0x0000
		self.skinCompoundId = read_ushort(f)			# 0xffff
		self.unkFlags = read_uint(f)
		self.unkFloat2List = [[read_float(f), read_float(f)] for i in range(32) if (self.unkFlags >> i) & 1]
class _subMeshUVScaleData():
	def __init__(self, f):
		read_fixed_byte_string(f, 3, 1, 0)
		self.uvIndex = read_byte(f)
		self.uvScale = read_ushort(f)
class _subMeshScaleData():
	def __init__(self, f):
		read_fixed_byte_string(f, 0x0c, 1, 0)
		self.translation = [read_ushort(f),read_ushort(f),read_ushort(f)]
		self.scale = [read_ushort(f),read_ushort(f),read_ushort(f)]
class _subMeshMaterial():
	def __init__(self, f):
		self.nodeId = read_ushort(f)
		self.materialParameterCount = read_uint(f)

		for x in range(self.materialParameterCount): _materialParameter(self)
class _materialParameter():
	def __init__(self, subMeshMaterial):
		self.dataName = read_fixed_string(f, read_uint(f))
		self.dataType = read_uint(f)
		self.data = self.getData(self.dataType)

		setattr(subMeshMaterial, self.dataName, self.data)

	def getData(self, dataType):
		match dataType:
			case 1:
				return read_uint(f)
			case 2:
				return read_float(f)
			case 3:
				return read_byte(f)
			case 4:
				return read_fixed_string(f,read_uint(f))
			case 6:
				return [read_fixed_byte_string(f, 0x08, 0, 0) for x in range(read_uint(f))]
			case 7:
				subMaterialParameter = _subMaterialParameter()
				subMaterialParameterCount = read_uint(f)
				for x in range(subMaterialParameterCount):  _materialParameter(subMaterialParameter)

				return subMaterialParameter
			case _:
				print("unknown dataType: {0:x}".format(dataType))
class _subMaterialParameter():
	pass

# print(len(sys.argv))
# print(sys.argv[1])

filePath = open_file()
# filePath = r""
filePath2 = filePath + "_data"
filePath3 = r"out.txt"

f = open(filePath, 'r+b')
g = open(filePath2, 'r+b')

fileSize = os.stat(filePath).st_size
fileSize2 = os.stat(filePath2).st_size

# print(filePath.split('\\')[-1])
# print(filePath2.split('\\')[-1])
# print(filePath)
# print(filePath2)

magic = read_fixed_string(f, 0x08)

f.seek(findNum(f,0x314D474F))
print("OGM1")

OGM1 = read_fixed_string(f, 4)
f.seek(0x08, 1)					# 0A 00 02 00 03 00 E3 03

nodeCount = read_uint(f)
sectionCount = read_uint(f)

nodeIdList = []
nodeFlagList = []
nodeParentIdList = []
nodeSiblingIdList = []
nodeSecondSiblingIdList = []
nodeChildIdList = []
nodeBoneIdList = []
nodeBoundBoxDataList = []
nodeExportInfoList = []

print("nodeCount: {0:x}	sectionCount:{1:x}".format(nodeCount, sectionCount))
print_here(f)
for x in range(sectionCount):
	sectionOffset = tell(f)
	sectionPresent = read_byte(f)	# normally 0 or 1, sometimes 2, subSectionCount?
	if sectionPresent != 0x00:
		match x:
			case 0x00:
				nodeIdList = [read_short(f) for y in range(nodeCount)]
			case 0x02:
				nodeFlagList = [readBits(f,read_ushort(f)) for y in range(nodeCount)]
			case 0x03:
				nodeParentIdList = [read_short(f) for y in range(nodeCount)]
			case 0x04:
				nodeSiblingIdList = [read_short(f) for y in range(nodeCount)]
			case 0x05:
				nodeSecondSiblingIdList = [read_short(f) for y in range(nodeCount)]
			case 0x06:
				nodeChildIdList = [read_short(f) for y in range(nodeCount)]
			case 0x07:
				nodeBoneIdList = [read_short(f) for y in range(nodeCount)]
			case 0x0b:
				# theres a shit ton of data in here. maybe it isn't just bound box data
				nodeFlagList2 = readBits(f,nodeCount)
				nodeBoundBoxDataList = [read_fixed_byte_string(f, 0x59, 0, 1) for x in range(sum(nodeFlagList2))]
				# print(len(nodeBoundBoxDataList))
			# case 0x0c:
			# 	unkFloats = [read_float(f) for y in range(nodeCount)]
			# 	print_here(f)
			case 0x11:
				nodeExportInfoList = [read_fixed_string(f, read_uint(f)) for y in range(nodeCount)]
				# for n in nodeExportInfoList:
				# 	print("\"{0}\"".format(n))
			case _:
				print("unknown section: {0:2x} @ {1:8x}".format(x, sectionOffset))
				break
	else:
		print("skipped section: {0:2x}".format(x))

nodeCount2 = read_uint(f)			# same as nodeCount
unk18 = read_byte(f)				# 0x01 / flag?
nodeDataList = [_nodeData(f) for x in range(nodeCount2)]

nodeNameList = ["None"] * nodeCount

nodeCount3 = read_uint(f)			# same as nodeCount - 1
unk19 = read_byte(f)				# 0x01 / flag?
nodeStringList = [read_fixed_string(f, read_uint(f)) for x in range(nodeCount3)]	# skips rootBoneIndex?

nodeCount4 = read_uint(f)			# same as nodeCount - 1
nodeIdList = [read_ushort(f) for x in range(nodeCount4)]							# skips rootBoneIndex

for x, nodeString in enumerate(nodeStringList):
	nodeNameList[nodeIdList[x]] = nodeString
	print("{0:4x} {1:4x} {2}".format(x, nodeIdList[x], nodeString))

nodeCount5 = read_uint(f)			# same as nodeCount
for x in range(nodeCount5):
	print(x)
	read_fixed_byte_string(f, 0x10, 0, 1)
	read_fixed_byte_string(f, 0x10, 0, 1)
	read_fixed_byte_string(f, 0x10, 0, 1)
	read_fixed_byte_string(f, 0x10, 0, 1)
	print()
	f.seek(-0x40, 1)

	m11 = read_float(f); m12 = read_float(f); m13 = read_float(f); m14 = read_float(f)
	m21 = read_float(f); m22 = read_float(f); m23 = read_float(f); m24 = read_float(f)
	m31 = read_float(f); m32 = read_float(f); m33 = read_float(f); m34 = read_float(f)
	m41 = read_float(f); m42 = read_float(f); m43 = read_float(f); m44 = read_float(f)

nodeCount6 = read_uint(f)			# same as nodeCount
for x in range(nodeCount6):
	m11 = read_float(f); m12 = read_float(f); m13 = read_float(f); m14 = read_float(f)
	m21 = read_float(f); m22 = read_float(f); m23 = read_float(f); m24 = read_float(f)
	m31 = read_float(f); m32 = read_float(f); m33 = read_float(f); m34 = read_float(f)
	m41 = read_float(f); m42 = read_float(f); m43 = read_float(f); m44 = read_float(f)

nodeCount7 = read_uint(f)			# same as nodeCount
unk20 = read_uint(f)				# 0x02 / subCount?
unk21 = read_byte(f)				# flag?
unkList3 = [read_ushort(f) for x in range(nodeCount7)]
# for unk in unkList3: print_hex(unk)
unk22 = read_byte(f)				# flag?
unkList4 = [read_ushort(f) for x in range(nodeCount7)]
# for unk in unkList4: print_hex(unk)

################################################################################################
# modelInfo
################################################################################################

unkId0 = read_ushort(f)
unkOffset6 = read_uint(f)			# points to unkId1

rootBoneIndex = read_ushort(f)
nodeCount8 = read_uint(f)			# same as nodeCount
bufferCount = read_uint(f)
meshCount = read_uint(f)
subMeshCount = read_uint(f)
unk25 = read_uint(f)				# null?
unk26 = read_uint(f)				# null?

print("rootBoneIndex: {0:x}	nodeCount: {1:x}	bufferCount: {2:x}	meshCount: {3:x}	subMeshCount: {4:x}".format(rootBoneIndex,nodeCount8,bufferCount,meshCount,subMeshCount))

unkId1 = read_ushort(f)				# 0x05
unkOffset7 = read_uint(f)			# points to unkId5

unkId2 = read_ushort(f)				# 0x00
unkOffset8 = read_uint(f)			# points to unkId4

lodCount = read_uint(f)
unk30 = read_uint(f)				# 0x01 / count?
unk31 = read_byte(f)				# 0x01 / flag?
lodBufferIdsList = [[read_uint(f) for z in range(read_uint(f))] for y in range(lodCount)]	# a list of buffer id's per lod
print("lodCount: {0:x}".format(lodCount))
# for bufferIds in lodBufferIdsList: print(bufferIds)

unkCount16 = read_uint(f)			# same as bufferCount / related to unk30?
unkId3 = read_uint(f)				# 0x02 / count?
unk33 = read_byte(f)				# 0x01 / flag?
bufferOffsetList = [read_ulonglong(f) for x in range(unkCount16)]
unk34 = read_byte(f)				# 0x01 / flag?
bufferLengthList = [read_ulonglong(f) for x in range(unkCount16)]

unkId4 = read_ushort(f)				# 0x02
unkOffset9 = read_uint(f)			# points to unkId5

nodeCount9 = read_uint(f)			# same as nodeCount
unkNodeList2 = [read_byte(f) for x in range(nodeCount9)]
print("unkCount14: {0:x}".format(nodeCount9))
# for unk in unkNodeList2: print_hex(unk)

################################################################################################
# bufferContainer
################################################################################################

unkId5 = read_ushort(f)				# 0x02
unkOffset10 = read_uint(f)			# points to unkId10

unkId6 = read_ushort(f)				# 0x00
unkOffset11 = read_uint(f)			# points to unkId7
bufferDataList = [readBits(f, read_ushort(f)) for x in range(bufferCount)] # describes the contents of the buffer
for bufferData in bufferDataList: print(bits_to_string(bufferData, 8))

# with open(filePath3, 'a') as file:
#     for bufferData in bufferDataList:
#         file.write(bits_to_string(bufferData, 8) + '\n')

unkId7 = read_ushort(f)				# 0x04
unkOffset12 = read_uint(f)			# points to unkId8
bufferDataList2 = [readBits(f, read_ushort(f)) for x in range(bufferCount)] # unknown data, only two flags
# for bufferData in bufferDataList2: print(bits_to_string(bufferData, 1))

# for x in range(bufferCount):
# 	print("{0} {1}".format(bits_to_string(bufferDataList[x], 8), bufferDataList2[x]))

unkId8 = read_ushort(f)				# 0x01
unkOffset13 = read_uint(f)			# points to unkId9
bufferStrideList = [read_ushort(f) for x in range(bufferCount)]

unkId9 = read_ushort(f)				# 0x02
unkOffset14 = read_uint(f)			# points to unkId10 / same as pointer as unkId5
bufferLengthList2 = [read_uint(f) for x in range(bufferCount)]

################################################################################################
# meshContainer
################################################################################################

unkId10 = read_ushort(f)			# 0x03
unkOffset15 = read_uint(f)			# points to unkId13

unkId11 = read_ushort(f)			# 0x02
unkOffset16 = read_uint(f)			# points to unkId12
meshDataList = [[_meshData(f) for y in range(read_byte(f))] for x in range(meshCount)]

unkId12 = read_ushort(f)			# 0x00
unkOffset17 = read_uint(f)			# points to unkId13 / same as pointer as unkId10
meshDataList2 = [readBits(f, read_ushort(f)) for x in range(meshCount)]
# for meshData in meshDataList2: print(bits_to_string(meshData))

################################################################################################
# subMeshContainer
################################################################################################

unkId13 = read_ushort(f)			# 0x04
unkOffset18 = read_uint(f)			# points to unkId19

unkId14 = read_ushort(f)			# 0x00
unkOffset19 = read_uint(f)			# points to unkId15
subMeshDataList = [_subMeshData(f) for x in range(subMeshCount)]

unkId15 = read_ushort(f)			# 0x01
unkOffset20 = read_uint(f)			# points to unkId16
meshIdList = [read_uint(f) for x in range(subMeshCount)]	# maps submeshes to mesh


unkId16 = read_ushort(f)			# 0x08
unkOffset21 = read_uint(f)			# points to unkId17
subMeshMaterialList = [_subMeshMaterial(f) for x in range(subMeshCount)]


unkId17 = read_ushort(f)			# 0x04
unkOffset22 = read_uint(f)			# points to unkId18
subMeshUVScaleDataList = [[_subMeshUVScaleData(f) for y in range(read_byte(f))] for x in range(subMeshCount)]	# some subMeshes have 2 uv's

unkId18 = read_ushort(f)			# 0x05
unkOffset23 = read_uint(f)			# points to unkId19
subMeshScaleDataList = [_subMeshScaleData(f) if meshDataList2[meshIdList[x]][3] == 1 else None for x in range(subMeshCount)]

# for x in range(subMeshCount):
# 	print(bits_to_string(meshDataList2[meshIdList[x]]))

unkId19 = read_ushort(f)			# 0xffff
unkOffset24 = read_uint(f)			# points to end of file



################################################################################################
# Doing stuff
################################################################################################

for x in range(subMeshCount):
	meshId = meshIdList[x]
	# print("meshId: {0:2x}".format(meshId))
	# print("subMesh: {0:3x}	vertexCount: {1:9x}	vertexOffset: {2:11x}	faceCount: {3:4x}	faceIndex: {4:4x}".format(x, subMeshDataList[x].vertexCount, subMeshDataList[x].vertexIndex, subMeshDataList[x].faceCount, subMeshDataList[x].faceIndex))
	meshFlags = meshDataList2[meshId]
	# print(meshFlags[7])
	# print(bits_to_string(meshFlags,8,False))
	# print(meshFlags)

	positionsList = []
	normalsList = []
	colorsList = []
	uv1List = []
	uv2List = []
	uv3List = []
	weightsList = []
	boneIdsList = []
	indexList = []

	vertexIndex = subMeshDataList[x].vertexIndex
	vertexCount = subMeshDataList[x].vertexCount

	faceIndex = subMeshDataList[x].faceIndex
	faceCount = subMeshDataList[x].faceCount

	meshName = "None"

	# per mesh are 3 mesh datas
	for y, meshData in enumerate(meshDataList[meshId]):

		bufferOffset = bufferOffsetList[meshData.bufferId]
		bufferLength = bufferLengthList[meshData.bufferId]
		bufferStride = bufferStrideList[meshData.bufferId]
		bufferFlags = bufferDataList[meshData.bufferId]

		lod = -1
		for lod, lodBufferIds in enumerate(lodBufferIdsList):
			for bufferId in lodBufferIds:
				if meshData.bufferId == bufferId:
					meshName = str(lod)
		
		vertexIndex = subMeshDataList[x].vertexIndex
		vertexCount = subMeshDataList[x].vertexCount

		faceIndex = subMeshDataList[x].faceIndex
		faceCount = subMeshDataList[x].faceCount

		subMeshScale = subMeshScaleDataList[x].scale if subMeshScaleDataList[x] != None else [1,1,1]
		submeshTranslation = subMeshScaleDataList[x].translation if subMeshScaleDataList[x] != None else [0,0,0]

		# print("bufferId: {0:2}	bufferOffset: {1:8x}	subBufferOffset: {2:8x} bufferStride: {3:4x} vertexIndex: {4:5x}".format(meshData.bufferId, bufferOffset, meshData.subBufferOffset, bufferStride, subMeshDataList[x].vertexIndex))
		print(bits_to_string(bufferFlags, 8, False))

		if bufferFlags[0] == 1:
			g.seek(bufferOffset + meshData.subBufferOffset + (subMeshDataList[x].vertexIndex * bufferStride))
			# if bufferFlags[0x03] == 1 and bufferFlags[0x7] == 1: print_here(g)
			for z in range(vertexCount):
				if z < 100: read_fixed_byte_string(g,bufferStride,1, 1)
				if bufferFlags[3] == 0:
					vx = read_float(g)
					vy = read_float(g)
					vz = read_float(g)
					vw = read_float(g)
					positionsList.append((vx,vy,vz))
					g.seek(bufferStride - 0x10, 1)
				if bufferFlags[3] == 1:
					# if z < 100 and bufferFlags[0x7] == 0 and bufferFlags[0x9] == 0: read_fixed_byte_string(g, bufferStride, 1, 1)
					vx = read_short(g) / 32767
					vy = read_short(g) / 32767
					vz = read_short(g) / 32767
					vw = read_short(g) / 32767
					positionsList.append((vx,vy,vz))
					g.seek(bufferStride - 0x08, 1)
		if bufferFlags[12] == 1:
			g.seek(bufferOffset + meshData.subBufferOffset + (subMeshDataList[x].vertexIndex * bufferStride))
			
			# if bufferFlags[0x03] == 1 and bufferFlags[0x7] == 1: print_here(g)
			for z in range(vertexCount):
				# if z < 100: read_fixed_byte_string(g,bufferStride,1, 1)
				
				g.seek(bufferStride, 1)
		if sum(bufferFlags) == 0:
			g.seek(bufferOffset + meshData.subBufferOffset + ((subMeshDataList[x].faceIndex * bufferStride)))
			for z in range(faceCount):
				fa = read_ushort(g) - vertexIndex
				fb = read_ushort(g) - vertexIndex
				fc = read_ushort(g) - vertexIndex

				indexList.append([fa,fb,fc])
	# print()


if f.tell() == fileSize:
	print("File fully read.")
else:
	print("Last read @ {0:x}".format(tell(f)))