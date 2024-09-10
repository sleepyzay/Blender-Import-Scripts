import sys
import os
from bindefs import *

print(__file__)

filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\101100_goku.dse\101100_goku.dse"
f = open(filePath, "rb")

f.seek(0x22)
boneCount = read_ushort(f)
meshCount = read_ushort(f)
meshCount2 = read_ushort(f)
matCount = read_ushort(f)
texCount = read_ushort(f)

boneDataOffset = read_uint(f)
boneDataOffset2 = read_uint(f)
meshDataOffset = read_uint(f)
meshDataOffset2 = read_uint(f)
matDataOffset = read_uint(f)
texDataOffset = read_uint(f)
stringBufferOffset = read_uint(f)

ukwOffset8 = read_uint(f)			#another baseOffset? / null
stringBufferOffset2 = read_uint(f)	#another baseOffset? / same as stringBufferOffset
stringBufferLength = read_uint(f)
fileNameOffset = read_uint(f)		#rel to stringBufferOffset
dataOffset8 = read_uint(f)
dataOffset9 = read_uint(f)			#texture?
fileEndOffset = read_uint(f)

baseOffset = tell(f)
print_hex(baseOffset)

print("boneCount: {0:x}	meshCount: {1:x}	matCount: {2:x}	texCount: {3:x}".format(boneCount, meshCount, matCount, texCount))


class _data1():
	def __init__(self, f):
		m11 = read_uint(f) / 4096.0 ; m12 = read_uint(f) / 4096.0 ; m13 = read_uint(f) / 4096.0
		m21 = read_uint(f) / 4096.0 ; m22 = read_uint(f) / 4096.0 ; m23 = read_uint(f) / 4096.0
		m31 = read_uint(f) / 4096.0 ; m32 = read_uint(f) / 4096.0 ; m33 = read_uint(f) / 4096.0
		m41 = read_uint(f) / 4096.0 ; m42 = read_uint(f) / 4096.0 ; m43 = read_uint(f) / 4096.0
class _data2():
	def __init__(self, f):
		self.ukw = read_ushort(f)			#0201
		self.ukw2 = read_uint(f)				#offset?
		self.ukw3 = read_ushort(f)			#0001
		self.boneNameOffset = read_uint(f)	#geoshape/geol
		self.boneParentID = read_ushort(f)
		self.boneSiblingID = read_ushort(f)
		self.boneOffset = read_uint(f)		#offset to element within data1
class _data3():
	def __init__(self, f):
		self.meshNameOffset = read_uint(f)
		self.meshOffset = read_uint(f)
		self.ukw = read_ushort(f)				#0x60/0x61
		self.ukw2 = read_byte(f)				#null
		self.ukw3 = read_byte(f)
		self.ukw4 = read_ushort(f)
		self.meshScale = (2 ^ (read_ushort(f)))
class _data4():
	def __init__(self, f):
		self.meshNameOffset = read_uint(f)
		self.meshBoneId = read_uint(f)
		self.meshId = read_uint(f)
		self.null = read_uint(f)
class _data5():
	def __init__(self, f):
		self.matNameOffset = read_uint(f)
		skip = f.seek(0x3, 1)
		self.ukwId = read_byte(f)
		skip2 = f.seek(0x08, 1)
		self.ukwId2 = read_byte(f)
		skip3 = f.seek(0x13, 1)
class _data6():
	def __init__(self, f):
		self.texPathOffset = read_uint(f)
		self.ukwOffset2 = read_uint(f)		#is after ukwOffset
		self.ukw = read_uint(f)
		self.ukwLength2 = read_uint(f)
		self.ukwOffset = read_uint(f)
		self.ukwLength = read_uint(f)
		self.ukw3 = read_short(f)			#texWidth?
		self.ukw4 = read_short(f)			#texHeight?
		self.null = read_uint(f)
		self.null2 = read_uint(f)
		self.ukw5 = read_short(f)			#always 4
		self.ukw6 = read_short(f)
		self.texNameOffset = read_uint(f)	#substring of texPath
		self.ukw7 = read_uint(f)				#length?
class _data8():
	def __init__(self, f):
		self.ukw = read_uint(f)				#longs?
		self.ukw2 = read_uint(f)
		self.ukw3 = read_uint(f)		

# fseek f (boneDataOffset + baseOffset) #seek_set
# boneDataArray = for x=1 to boneCount collect (data = data1())

f.seek(boneDataOffset + baseOffset)
boneDataList = [_data1(f) for x in range(boneCount)]

f.seek(boneDataOffset2 + baseOffset)
boneDataList2 = [_data2(f) for x in range(boneCount)]

f.seek(meshDataOffset + baseOffset)
meshDataList = [_data3(f) for x in range(meshCount)]
	
f.seek(meshDataOffset2 + baseOffset)
meshData2List = [_data4(f) for x in range(meshCount2)]

f.seek(matDataOffset + baseOffset)
matDataList = [_data5(f) for x in range(matCount)]

f.seek(texDataOffset + baseOffset)
texDataList = [_data6(f) for x in range(texCount)]
	
f.seek(dataOffset8)
ukwData8List = [_data8(f) for x in range(boneCount)]

class _sectionHeader():
	def __init__(self, f):
		self.type = read_byte(f)
		self.ukw = read_byte(f)
		self.ukw2 = read_byte(f)
		self.ukw3 = read_byte(f)
		self.length = read_uint(f)
		

for x in range(meshCount):
	meshData = meshDataList[x]
	meshData2 = meshData2List[x]
	f.seek(meshData.meshOffset + baseOffset)

	meshHeader = None

	vertSum = 0
	while True:
	# for x in range(1):
		# ReadFixedByteString f 0x08 1 0
		read_fixed_byte_string(f, 0x08, 1, 0)
		sectionHeader = _sectionHeader(f)

		if sectionHeader.type in (0x03, 0x04):
			sectionOffset = tell(f)
			read_fixed_byte_string(f, 0x18, 1, 0)
			vertexCount = read_short(f)
			vertexStride = read_byte(f)
			vertexType = read_byte(f)
			ukw4 = read_uint(f)		# only see it as non null if ukw2 is non null
			
			boneMap = [read_short(f) for x in range(sectionHeader.ukw3)]
			f.seek(0x10 - (2 * sectionHeader.ukw3), 1) #seek_cur	--array w/ length of ukw2?, byte aligned?

			print("{0:x} {1:x} {2:08b}".format(vertexStride, vertexType, vertexType))
			# 0 - pos
			# 1 - 
			# 2 - u1h, n1, n2
			# 3 - uvs
			# 4 - weights
			# 5 - u1b-u4b
			# 6 - 
			# 7 - 
			# for x in range(10):
			# 	read_fixed_byte_string(f, vertexStride, 0, 1)






			f.seek(sectionOffset + sectionHeader.length - 0x08)

		elif sectionHeader.type == 0x02:
			meshHeader = sectionHeader
		elif sectionHeader.type == 0x01:
			# print("")
			break
		else:
			# Handle unexpected section type
			print("Oops! Unexpected sectionType:", sectionHeader.type)


print("Last read @ {0:x}".format(tell(f)))
f.close()