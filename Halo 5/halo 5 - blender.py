import io
import sys
import mmh3
import math
import struct
import uuid
import os
import bpy
import mathutils
from mathutils import Matrix, Quaternion, Vector

def clean_scene():      #stolen
	for item in bpy.data.objects:
		if item.type == 'MESH' or item.type == 'EMPTY':
			bpy.data.objects.remove(item)

	check_users = False
	for collection in (
		bpy.data.meshes, 
		bpy.data.armatures, 
		bpy.data.materials, 
		bpy.data.textures, 
		bpy.data.images, 
		bpy.data.collections
	):
		 for item in collection:
			 if item.users == 0 or not check_users:
				 collection.remove(item)
				 
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

def unpackNormals(file_object):
	normals = read_uint(file_object)
	xn = (normals & 0x3ff)
	yn = ((normals >> 10) & 0x3ff)
	zn = ((normals >> 20) & 0x3ff)
	wn = (normals >> 30) & 0x3
	xn = (xn / 1023) * 2 - 1
	yn = (yn / 1023) * 2 - 1
	zn = (zn / 1023) * 2 - 1

	wn = wn - 2
	normalFactor = (wn > 0) - (wn < 0)
	normalFactor = 1
	# print(normalFactor)

	return (normalFactor * xn, normalFactor * yn, normalFactor * zn)

def read_udec4n_2(file_object):
	normal = read_uint(file_object)
	nx = (((normal >> 0) & 0x3FF) / 1023) * 2 - 1
	ny = (((normal >> 10) & 0x3FF) / 1023) * 2 - 1
	nz = (((normal >> 20) & 0x3FF) / 1023) * 2 - 1
	return (nx,ny,nz)

def read_udec4n(file_object):
	normal = read_uint(file_object)
	a = (((normal >> 0) & 0x3FF) / 1023) - 0.5
	b = (((normal >> 10) & 0x3FF) / 1023) - 0.5
	c = (((normal >> 20) & 0x3FF) / 1023) - 0.5
	d = (1 - (a * a - b * b - c * c))
	e = (normal >> 30)
	#print("{0:032b}".format(normal))
	
	if e == 0:
		return Quaternion([d, a, b, c]).to_axis_angle()[0]
	if e == 1:
		return Quaternion([a, d, b, c]).to_axis_angle()[0]
	if e == 2:
		return Quaternion([a, b, d, c]).to_axis_angle()[0]
	if e == 3:
		return Quaternion([a, b, c, d]).to_axis_angle()[0]
def normalize_tuple(t):
    """
    Normalizes a tuple (vector) so that its length is 1.

    :param t: The tuple to normalize (e.g., (x, y, z) or (r, g, b, a)).
    :return: A normalized tuple with the same number of components.
    """
    magnitude = math.sqrt(sum(component ** 2 for component in t))
    if magnitude == 0:
        return t  # Avoid division by zero; return original tuple
    return tuple(component / magnitude for component in t)
class _table1():    # materials?, shaders?
	def __init__(self, file_object):
		self.tagType = read_fixed_string(file_object, 4)[::-1]
		self.stringOffset = read_uint(file_object)
		self.hash = read_uint(file_object)
		self.hash2 = read_uint(file_object)
		self.hash3 = read_uint(file_object)
		self.null = read_uint(file_object)  #0xff's, probably also hashpo
class _table2():    # offsetTable?
	def __init__(self, file_object):
		self.length = read_uint(file_object)
		self.ukw = read_ushort(file_object)
		self.ukwID = read_ushort(file_object)   #0x01 = info, 0x02 = resource
		self.offset = read_uint(file_object)
		self.null = read_uint(file_object)
class _table3():    # infoTable?
	def __init__(self, file_object):
		self.hash = read_uint(file_object)
		self.hash2 = read_uint(file_object)
		self.hash3 = read_uint(file_object)
		self.hash4 = read_uint(file_object)
		self.ukw = read_ushort(file_object)
		self.ukw2 = read_ushort(file_object)
		self.dataID = read_uint(file_object)            #data pointer
		self.infoID = read_uint(file_object)            #info pointer
		self.table2SubOffset = read_uint(file_object)   #data offset
class _table4():    # reourceTable?
	def __init__(self, file_object):
		self.bufferType = read_ulonglong(file_object)             #1 = vert, 2 = face
		self.table2ID = read_uint(file_object)
		self.table2ID2 = read_uint(file_object)
		self.table2SubOffset = read_uint(file_object)
class _table5():    # materials?, shaders?
	def __init__(self, file_object):
		self.table2ID = read_uint(file_object)
		self.table2SubOffset = read_uint(file_object)
		self.stringOffset = read_uint(file_object)
		self.table1ID = read_uint(file_object)
class _stringTable():
	def __init__(self, file_object):
		self.ukwID = read_uint(file_object)
		self.stringOffset = read_uint(file_object)
class _unknownData():   # resource group data?
	def __init__(self, file_object):
		#file_object.seek(self.ukwDataLength, 1)
		self.ukwDataOffset = tell(file_object)

		self.tableCount = read_ulonglong(file_object)
		self.tableOffset = read_ulonglong(file_object) + self.ukwDataOffset
		for x in range(self.tableCount):
			file_object.seek(self.tableOffset + x * 0x28)
			ukwHash = read_ulonglong(file_object)   #index 1 = no_geo 2 = __default__
			print_hex(ukwHash)
			# resourceIDCount = read_ulonglong(file_object)
			# resourceIDOffset = read_ulonglong(file_object) + self.ukwDataOffset	#first table always 0, second always total resource count
			# ukwCount = read_ulonglong(file_object)
			# ukwOffset = read_ulonglong(file_object) + self.ukwDataOffset
		#more data here based on data in loop but prob not necassary

class _header():
	def __init__(self, file_object):
		self.tagType = read_fixed_string(file_object, 4)[::-1]
		self.ukw = read_uint(file_object)
		self.hash = read_uint(file_object)
		self.hash2 = read_uint(file_object)
		self.hash3 = read_uint(file_object)
		self.hash4 = read_uint(file_object)
		self.hash5 = read_uint(file_object)
		self.table1Count = read_uint(file_object)
		self.table2Count = read_uint(file_object)
		self.table3Count = read_uint(file_object)
		self.table4Count = read_uint(file_object)
		self.table5Count = read_uint(file_object)
		self.stringCount = read_uint(file_object)
		self.stringBufferLength = read_uint(file_object)
		self.ukwDataLength = read_uint(file_object)
		self.infoOffset = read_uint(file_object)
		self.infoLength = read_uint(file_object)
		self.resourceLength = read_uint(file_object)
		self.ukw2 = read_uint(file_object)
		self.ukw3 = read_uint(file_object)

		self.stringBufferOffset = tell(file_object) + (self.table1Count * 0x18) + (self.table2Count * 0x10) + (self.table3Count * 0x20) + (self.table4Count * 0x14) + (self.table5Count * 0x10) + (self.stringCount * 0x08)
		self.ukwDataOffset = self.stringBufferOffset + self.stringBufferLength
		self.resourceOffset = (self.infoOffset + self.infoLength)

class renderModelBlock():
	def __init__(self, parent_object, file_object, subOffset):                #prob reading garbage data by immediately initializing
		file_object.seek(subOffset)
		parent_object.renderModel = self 
		
		self.null = read_uint(file_object)
		self.null2 = read_uint(file_object)
		self.ukw = read_uint(file_object)           #offset/length?
		file_object.seek(0x04, 1)                   #padding
		self.nameHash = read_uint(file_object)
		self.flags = read_ushort(file_object)
		self.version = read_ushort(file_object)
		self.meshResourcePackingPolicy = read_uint(file_object)                 # 0 = single resource, 1 = multiple resource
		self.runtimeImportInfoChecksum = read_uint(file_object)
class renderModelRegionBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.regionCount = read_uint(file_object)

		self.nameHash = []
		for x in range(self.regionCount):
			file_object.seek(subOffset + x * 0x20)
			self.nameHash.append(read_uint(file_object))
			file_object.seek(0x1c, 1)   #accessed later by renderModelPermutation

		self.renderModelPermutation = []

		parent_object.renderModelRegion = self
class renderModelPermutationBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class permutation():
			def __init__(self, file_object):
				self.nameHash = read_uint(file_object)
				self.meshIndex = read_ushort(file_object)
				self.meshCount = read_ushort(file_object)

		file_object.seek(subOffset2 + 0x10)
		self.permutationCount = read_uint(file_object)
		
		self.permutation = []
		for x in range(self.permutationCount):
			file_object.seek(subOffset + x * 0x1c)
			self.permutation.append(permutation(file_object))

		parent_object.renderModelPermutation.append(self)     
class renderModelNodeBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class node():
			def __init__(self, file_object):
				self.nodeNameHash = read_uint(file_object)
				self.parentNode = read_short(file_object)
				self.firstChildNode = read_short(file_object)
				self.nextSiblingNode = read_short(file_object)
				self.flags = read_ushort(file_object)
				self.defaultTranslation = read_vec3(file_object)
				self.defaultRotation = read_vec4(file_object)
				self.inverseScale = read_float(file_object)
				self.inverseForward = read_vec3(file_object)
				self.inverseLeft = read_vec3(file_object)
				self.inverseUp = read_vec3(file_object)
				self.inversePosition = read_vec3(file_object)
				self.distanceFromParent = read_float(file_object)
				self.procedure = read_byte(file_object)              #constraints
				self.procedureAxis = read_byte(file_object)
				self.procedureIndex = read_byte(file_object)
				file_object.seek(0x01, 1)   #padding
				self.procedureNodeA = read_ushort(file_object)
				self.procedureNodeB = read_ushort(file_object)
				self.procedureVar1 = read_float(file_object)
				self.procedureVar2 = read_float(file_object)
				self.procedureNeutralOffset = read_vec3(file_object)      

		file_object.seek(subOffset2 + 0x10)
		self.nodeCount = read_uint(file_object)
		self.nodeList = []

		file_object.seek(subOffset)
		for x in range(self.nodeCount):
			file_object.seek(subOffset + (x * 0x7c))
			self.nodeList.append(node(file_object))

		parent_object.renderModelNode = self 
class renderModelMarkerGroupBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.markerGroupCount = read_uint(file_object)

		self.nameHash = []
		for x in range(self.markerGroupCount):
			file_object.seek(subOffset + x * 0x20)
			self.nameHash.append(read_uint(file_object))
			file_object.seek(0x1c, 1)   #accessed later by renderModelMarker

		self.renderModelMarker = []

		parent_object.renderModelMarkerGroup = self
class renderModelMarkerBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class marker():
			def __init__(self, file_object):
				file_object.seek(subOffset + x * 0x38)
				self.regionIndex = read_byte(file_object)
				file_object.seek(3, 1)  #skip padding
				self.permutationIndex = read_uint(file_object)
				self.nodeIndex = read_byte(file_object)
				self.flags = read_byte(file_object)
				file_object.seek(2, 1)  #skip padding
				self.pos = read_vec3(file_object)
				self.rot = read_vec4(file_object)
				self.scl = read_float(file_object)
				self.dir = read_vec3(file_object)                               
		
		file_object.seek(subOffset2 + 0x10)
		self.markerCount = read_uint(file_object)
		
		self.marker = []
		for x in range(self.markerCount):
			self.marker.append(marker(file_object))

		parent_object.renderModelMarker.append(self)       
class globalGeometryMaterialBlock():    #todo
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.materialCount = read_uint(file_object)

		for x in range(self.materialCount):
			file_object.seek(subOffset + x * 0x20)
			read_fixed_byte_string(file_object, 0x20, 1, 0)
			file_object.seek(0x08,1)    #padding

		parent_object.globalGeometryMaterial = self
class globalMeshBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.meshCount = read_uint(file_object)

		self.lodRenderData = []                         # other 3 blocks generally arent used, listing anyways
		self.globalInstanceBucketBlock = []
		self.indicesWordBlock = []
		self.vertexKeyBlock = []

		parent_object.globalMesh = self
class lodRenderDataBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.partBlockCount = read_uint(file_object)
		file_object.seek(0x08, 1)                       #null
		self.meshFlags = read_ushort(file_object)
		self.rigidNodeIndex = read_byte(file_object)
		self.vertexType = read_byte(file_object)
		self.useDualQuat = read_byte(file_object)
		self.indexBufferType = read_byte(file_object)
		self.pcaMeshIndex = read_ushort(file_object)

		#print("{0:2x}    {1:2x}".format(self.vertexType, self.rigidNodeIndex))

		file_object.seek(subOffset + 0x70)                          #first 0x70 is accessed by children of lodRenderData
		self.vertexBufferIndex = [                                  #so far I've only seen the first one used, the rest are ff's
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object),
			read_ushort(file_object)]
		self.indexBufferIndex = read_ushort(file_object)
		self.lodFlags = read_ushort(file_object)
		file_object.seek(0x02, 1)                              #padding
		parent_object.lodRenderData.append(self)   
class partBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class part():
			def __init__(self, file_object):
				self.materialIndex = read_ushort(file_object)
				self.transparentSortingIndex = read_ushort(file_object)
				self.indexStart = read_uint(file_object)
				self.indexCount = read_uint(file_object)
				self.subPartStart = read_ushort(file_object)
				self.subPartCount = read_ushort(file_object)
				self.partType = read_byte(file_object)
				self.specializedRender = read_byte(file_object)
				self.partFlags = read_uint(file_object)
				self.budgetVertexCount = read_ushort(file_object)
				file_object.seek(0x02, 1)   #padding

		file_object.seek(subOffset2 + 0x10)
		self.partCount = read_uint(file_object)

		self.parts = []
		for x in range(self.partCount):
			file_object.seek(subOffset + x * 0x18)
			self.parts.append(part(file_object))

		parent_object[-1].partBlock = self
class subPartBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class subPart():
			def __init__(self, file_object):
				self.indexStart = read_uint(file_object)
				self.indexCount = read_uint(file_object)
				self.partIndex = read_ushort(file_object)
				self.budgetVertexCount = read_ushort(file_object)
				self.analyticalLightIndex = read_uint(file_object)

		file_object.seek(subOffset2 + 0x10)
		self.subPartCount = read_uint(file_object)

		self.subParts = []
		for x in range(self.subPartCount):
			file_object.seek(subOffset + (x * 0x10))
			self.subParts.append(subPart(file_object))

		parent_object[-1].partBlock = self
class pcaMeshIndexBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.pcaMeshIndexCount = read_uint(file_object)

		self.pcaMeshIndex = []
		for x in range(self.pcaMeshIndexCount):
			file_object.seek(subOffset + x * 0x04)      #i know it's redundant fuck you
			self.pcaMeshIndex.append(read_uint(file_object))

		parent_object.pcaMeshIndex = self
class compressionInfoBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class compressionInfo():
			def __init__(self, file_object):
				self.compressionFlags = read_ushort(file_object)
				file_object.seek(0x02, 1)                         #padding
				self.position_bounds_x0 = read_float(file_object)
				self.position_bounds_x1 = read_float(file_object)
				self.position_bounds_y0 = read_float(file_object)
				self.position_bounds_y1 = read_float(file_object)
				self.position_bounds_z0 = read_float(file_object)
				self.position_bounds_z1 = read_float(file_object)
				self.texcoord_bounds_u0 = read_float(file_object)
				self.texcoord_bounds_u1 = read_float(file_object)
				self.texcoord_bounds_v0 = read_float(file_object)
				self.texcoord_bounds_v1 = read_float(file_object)
				self.unused0 = read_float(file_object)
				self.unused1 = read_float(file_object)
	
		file_object.seek(subOffset2 + 0x10)
		self.compressionInfoCount = read_uint(file_object)   #should prob name boundBoxCount

		self.compressionInfo = []
		for x in range(self.compressionInfoCount):           #only 1, prob always 1
			file_object.seek(subOffset + (x * 0x34))
			self.compressionInfo.append(compressionInfo(file_object))

		parent_object.compressionInfo = self
class meshResourceGroupBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		file_object.seek(subOffset2 + 0x10)
		self.resourceCount = read_uint(file_object)

		self.meshResourceGroup = []
		for x in range(self.resourceCount):
			file_object.seek(subOffset + x * 0x10)

			file_object.seek(0x0c, 1)       #padding
			self.meshResourceGroup.append(read_uint(file_object))

		parent_object.meshResourceGroup = self
class meshResourceGroupLookUpBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class groupLookup(object):
			def __init__(self, file_object):
				self.resourceGroupIndex = read_ushort(file_object)
				self.groupItemIndex = read_ushort(file_object)

		file_object.seek(subOffset2 + 0x10)
		self.lookUpCount = read_uint(file_object)

		self.meshResourceGroupLookUp = []
		file_object.seek(0x0c, 1)       #padding
		for x in range(self.lookUpCount):
			file_object.seek(subOffset + x * 0x04)
			self.meshResourceGroupLookUp.append(groupLookup(file_object))

		parent_object.meshResourceGroupLookUp = self    
class defaultNodeOrientationsBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class node():
			def __init__(self, file_object):
				self.rotation =      read_vec4(file_object)
				self.translation =   read_vec3(file_object)
				self.scale =         read_float(file_object)

		file_object.seek(subOffset2 + 0x10)
		self.nodeCount = read_uint(file_object)
		
		self.defaultNodeOrientations = []
		for x in range(self.nodeCount):
			file_object.seek(subOffset + x * 0x20)
			self.defaultNodeOrientations.append(node(file_object))
			
		parent_object.defaultNodeOrientations = self
class vertexBuffersBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class vertexBuffers():
			def __init__(self, file_object):
				#read_fixed_byte_string(file_object, 0x18, 1, 1)
				self.declarationType = read_byte(file_object)    #0x02,0x03,0x28
				self.stride = read_byte(file_object)
				file_object.seek(0x02, 1)                   #padding
				self.count = read_uint(file_object)
				self.length = read_uint(file_object)
				self.ukwID = read_uint(file_object)         #always 1
				self.null = read_uint(file_object)
				self.null2 = read_uint(file_object)
				file_object.seek(0x38, 1)   #accessed later by elements in table4
				
		file_object.seek(subOffset2 + 0x10)
		self.vertexBuffersCount = read_uint(file_object)

		self.vertexBuffers = []
		for x in range(self.vertexBuffersCount):
			file_object.seek(subOffset + x * 0x50)
			self.vertexBuffers.append(vertexBuffers(file_object))

		parent_object.vertexBuffers = self
class indexBuffersBlock():
	def __init__(self, parent_object, file_object, subOffset, subOffset2):
		class indexBuffers():
			def __init__(self, file_object):
				self.declarationType = read_byte(file_object)
				self.stride = read_byte(file_object)
				file_object.seek(0x02, 1)                   #padding
				self.count = read_uint(file_object)
				self.length = read_uint(file_object)
				self.ukw2 = read_uint(file_object)
				self.null = read_uint(file_object)
				self.null2 = read_uint(file_object)
				file_object.seek(0x30, 1)   #accessed later by elements in table4     

		file_object.seek(subOffset2 + 0x10)
		self.indexBuffersCount = read_uint(file_object)

		self.indexBuffers = []
		for x in range(0,self.indexBuffersCount):
			file_object.seek(subOffset + x * 0x48)
			self.indexBuffers.append(indexBuffers(file_object))

		parent_object.indexBuffers = self

class modelFile():
	def __init__(self, file_object):
		_header.__init__(self,file_object)  #inheret properties from header class initialised on this line

		debugPrint = False

		self.table1Array=[]
		self.table2Array=[]
		self.table3Array=[]
		self.table4Array=[]
		self.table5Array=[]
		self.stringTableArray=[]
		for x in range(self.table1Count):
			if (x==0 and debugPrint == True):print("table1 @ {0:8x}    count: {1:4x}    length: {2:8x}".format(tell(file_object), self.table1Count, self.table1Count * 0x20))
			#read_fixed_byte_string(file_object, 0x18, 1, 0)
			self.table1Array.append(_table1(file_object))
		for x in range(self.table2Count):
			if (x==0 and debugPrint == True):print("table2 @ {0:8x}    count: {1:4x}    length: {2:8x}".format(tell(file_object), self.table2Count, self.table2Count * 0x10))
			#read_fixed_byte_string(file_object, 0x10, 1, 0)
			self.table2Array.append(_table2(file_object))
		for x in range(self.table3Count):
			if (x==0 and debugPrint == True):print("table3 @ {0:8x}    count: {1:4x}    length: {2:8x}".format(tell(file_object), self.table3Count, self.table3Count * 0x20))
			#read_fixed_byte_string(file_object, 0x20, 1, 0)
			self.table3Array.append(_table3(file_object))
		for x in range(self.table4Count):
			if (x==0 and debugPrint == True):print("table4 @ {0:8x}    count: {1:4x}    length: {2:8x}".format(tell(file_object), self.table4Count, self.table4Count * 0x14))
			#read_fixed_byte_string(file_object, 0x14, 1, 1)
			self.table4Array.append(_table4(file_object))
		for x in range(self.table5Count):
			if (x==0 and debugPrint == True):print("table5 @ {0:8x}    count: {1:4x}    length: {2:8x}".format(tell(file_object), self.table5Count, self.table5Count * 0x10))
			#read_fixed_byte_string(file_object, 0x10, 1, 0)
			self.table5Array.append(_table5(file_object))
		for x in range(self.stringCount):
			if (x==0 and debugPrint == True):print("stringTable @ {0:x} count: {1:2x}    length: {2:x}".format(tell(file_object), self.stringCount, self.stringBufferLength))
			#read_fixed_byte_string(file_object, 0x08, 1, 0)
			self.stringTableArray.append(_stringTable(file_object))

		self.nameHashDict={}
		if debugPrint == True:print("stringBufferOffset @ {0:x}, length: {1:x}".format(tell(file_object),self.stringBufferLength))
		# for x in range(self.stringCount):
		#     file_object.seek(self.stringBufferOffset + self.stringTableArray[x].stringOffset)
		#     string = read_string(file_object)
		#     nameHashDict[string]=mmh3.hash(string,signed=False)
		while tell(file_object) < self.ukwDataOffset:  #string table dosent parse all strings
			string = read_string(file_object)
			self.nameHashDict[string]=mmh3.hash(string,signed=False)
			#print("{0:8x} {1}".format(nameHashDict[string], string))
		
		if debugPrint == True:print("ukwDataOffset @ {0:x} ukwDataLength: {1:x}".format(self.ukwDataOffset, self.ukwDataLength))
		#self.unknownData = _unknownData(file_object)
		file_object.seek(self.ukwDataOffset + self.ukwDataLength)

		# render_model_region_block
		#    render_model_permutation_block
		# render_model_node_block
		# render_model_marker_group_block
		#    render_model_marker_block
		# global_geometry_material_block
		# global_mesh_block
		#    LODRenderDataBlock
		#        per_mesh_raw_data_block
		#        sorting_position_block
		#        part_block
		#        subpart_block
		#    global_instance_bucket_block
		#    indices_word_block
		#    vertexKeyBlock
		# pcaMeshIndexBlock
		# compression_info_block
		# MeshResourceGroup_BlockSchema
		# default_node_orientations_block

		# vertex_buffers_block
		# index_buffers_block 

		# print("infoOffset: {0:x} infoLength: {1:x}".format(self.infoOffset, self.infoLength))
		# print("resourceOffset: {0:x} resourceLength: {1:x}".format(self.resourceOffset, self.resourceLength))
		
		for table3 in self.table3Array:
			subOffset = 0   #data
			subOffset2 = 0  #info
			if (table3.dataID != 0xffffffff):subOffset = self.table2Array[table3.dataID].offset + self.infoOffset
			if (table3.infoID != 0xffffffff):subOffset2 = self.table2Array[table3.infoID].offset + self.infoOffset + table3.table2SubOffset #infoSubOffset?

			match table3.hash:
				case 0x69ff7dc3:renderModelBlock             (self, file_object, subOffset)
				case 0x5f23bc11:renderModelRegionBlock       (self, file_object, subOffset, subOffset2)
				case 0x7900dde2:renderModelPermutationBlock  (self.renderModelRegion, file_object, subOffset, subOffset2)
				case 0xc01e3aa5:pass    # global_render_model_instance_placement_block              / -1
				case 0xb74453b7:renderModelNodeBlock         (self, file_object, subOffset, subOffset2)
				case 0x57a4d1a3:pass    # BonePhysicsDefinitionBlock                                / -1
				case 0xe60694fa:renderModelMarkerGroupBlock  (self, file_object, subOffset, subOffset2)
				case 0xd7cc940f:renderModelMarkerBlock       (self.renderModelMarkerGroup, file_object, subOffset, subOffset2)
				case 0xb1135973:globalGeometryMaterialBlock  (self, file_object, subOffset, subOffset2)
				case 0x3cbb78d5:pass    # global_error_report_categories_block                      / -1
				case 0x67fac496:pass    # MeshImportInfoBlock                                       / -1
				case 0xebb348bb:globalMeshBlock              (self, file_object, subOffset, subOffset2)
				case 0x67fac497:lodRenderDataBlock           (self.globalMesh, file_object, subOffset, subOffset2)
				case 0x52900ab0:pass    # per_mesh_raw_data_block                                   / -1
				case 0x684ef46d:pass    # sorting_position_block                                    / -1
				case 0x4a81849d:partBlock                    (self.globalMesh.lodRenderData, file_object, subOffset, subOffset2)
				case 0x09109a33:subPartBlock                 (self.globalMesh.lodRenderData, file_object, subOffset, subOffset2)
				case 0x0c556069:pass    # global_instance_bucket_block                              / -1
				case 0x92f5e99b:pass    # indices_word_block                                        / -1
				case 0xdad1c118:pass    # vertexKeyBlock                                            / -1
				case 0x47c61323:pcaMeshIndexBlock            (self, file_object, subOffset, subOffset2)
				case 0xfe51fdac:compressionInfoBlock         (self, file_object, subOffset, subOffset2)
				case 0xc23b2003:pass    # per_mesh_node_map_block                                   / -1
				case 0x06360432:pass    # per_mesh_subpart_visibility_block                         / -1
				case 0xadd17af6:pass    # lightmap_definition_texcoords_block                       / -1
				case 0x79487d4e:pass    # per_instance_per_chart_lightmap_texcooord_transform_block / -1
				case 0xc8d81a34:pass    # per_instance_lightmap_texcoord_transform_indices_block    / -1
				case 0xf28eacd0:pass    # water_bounding_box_block                                  / -1
				case 0xf74ac124:pass    # RenderGeometryAnimatedMeshRef_BlockSchema                 / -1
				case 0xd7cc9a5e:pass    # render_geometry_lod_volume_block                          / -1
				case 0x211c66f6:meshResourceGroupBlock       (self, file_object, subOffset, subOffset2)
				case 0x8aeb8021:pass    # render_geometry_api_resource_definition_struct / related to MeshResourceGroup_BlockSchema / x of resourceCount / table3.ukwID = 2
				case 0xb12cfdd4:meshResourceGroupLookUpBlock (self, file_object, subOffset, subOffset2) #there are two of these, one for verts and for faces, will read twice overwriting the first but they are exactly the same so it wont matter
				case 0x1119acfd:pass    # instance_node_map_mapping_block                           / -1
				case 0xa3a5979b:defaultNodeOrientationsBlock (self, file_object, subOffset, subOffset2)
				case 0x0cece183:pass    # RenderModelBoneGroupBlock                                 / -1
				case 0x558222ea:pass    # RenderModelClothMeshBlock                                 / -1
				case 0x74da5cd4:pass    # RenderModelClothDataBlock                                 / -1
				case 0x10dd7329:vertexBuffersBlock           (self, file_object, subOffset, subOffset2)
				case 0xc747c29e:indexBuffersBlock            (self, file_object, subOffset, subOffset2)
				case _:
					print("Undefined guid found: {0:x}".format(table3.hash))

def importModel(filePath):
	modelScale = 1                        #todo make editable in import menu
	
	f = open(filePath, "rb")
	render_model = modelFile(f)

	print("globalMeshCount: {0:2d}".format(render_model.globalMesh.meshCount))
	print("pcaMeshCount:    {0:2d}  {1}".format(render_model.pcaMeshIndex.pcaMeshIndexCount, render_model.pcaMeshIndex.pcaMeshIndex))
	print("resourceCount:   {0:2d}".format(render_model.meshResourceGroup.resourceCount))
	print("packingPolicy:   {0:2d}".format(render_model.renderModel.meshResourcePackingPolicy))

	##################################################################
	# Skeleton
	##################################################################
	armature_obj = bpy.data.objects.new("Armature", bpy.data.armatures.new("Armature"))     #create armature object
	bpy.context.scene.collection.objects.link(armature_obj)                                 #link armature object to scene
	bpy.context.view_layer.objects.active = armature_obj                                    #focus on armature object
	bpy.ops.object.mode_set(mode='EDIT')                                                    #set scene to edit mode

	armature_obj.show_in_front = False

	for x in range(render_model.renderModelNode.nodeCount):
		node = render_model.renderModelNode.nodeList[x]
		bone = armature_obj.data.edit_bones.new(get_key(node.nodeNameHash, render_model.nameHashDict))
		
		m11 = node.inverseForward[0]; m12 = node.inverseLeft[0]; m13 = node.inverseUp[0]; m14 = node.inversePosition[0]
		m21 = node.inverseForward[1]; m22 = node.inverseLeft[1]; m23 = node.inverseUp[1]; m24 = node.inversePosition[1]
		m31 = node.inverseForward[2]; m32 = node.inverseLeft[2]; m33 = node.inverseUp[2]; m34 = node.inversePosition[2]
		
		rot = Matrix(([m11, m12, m13],[m21, m22, m23],[m31, m32, m33]))
		pos = Vector([m14, m24, m34]) * modelScale
		scl = Vector([node.inverseScale,node.inverseScale,node.inverseScale])
		
#        print("{1:3} {0}".format(bone.name,x))
		
		bone.tail = bone.tail + Vector([0,0.025,0])
		bone.matrix = Matrix.LocRotScale(pos,rot,scl).inverted() 
		
		if node.parentNode > -1:
			bone.parent = armature_obj.data.edit_bones[node.parentNode]
			
	bpy.ops.object.mode_set(mode = 'OBJECT')
	
#    for x in range(render_model.renderModelNode.nodeCount):
#        print("{1:3} {0}".format(armature_obj.data.bones[x].name, x))
	
	boundPosScale = Vector([
		(render_model.compressionInfo.compressionInfo[0].position_bounds_x1 - render_model.compressionInfo.compressionInfo[0].position_bounds_x0),
		(render_model.compressionInfo.compressionInfo[0].position_bounds_y1 - render_model.compressionInfo.compressionInfo[0].position_bounds_y0),
		(render_model.compressionInfo.compressionInfo[0].position_bounds_z1 - render_model.compressionInfo.compressionInfo[0].position_bounds_z0)])
	boundUVScale = Vector([
		(render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u1 - render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0),
		(render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v1 - render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0)]
	)
	
#    print("{0} {1}".format(render_model.compressionInfo.compressionInfo[0].position_bounds_x0, render_model.compressionInfo.compressionInfo[0].position_bounds_x1))
#    print("{0} {1}".format(render_model.compressionInfo.compressionInfo[0].position_bounds_y0, render_model.compressionInfo.compressionInfo[0].position_bounds_y1))
#    print("{0} {1}".format(render_model.compressionInfo.compressionInfo[0].position_bounds_z0, render_model.compressionInfo.compressionInfo[0].position_bounds_z1))
#    print("{0} {1}".format(render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0, render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u1))
#    print("{0} {1}".format(render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0, render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v1))

	##################################################################
	# Markers
	##################################################################
#    for x in range(render_model.renderModelMarkerGroup.markerGroupCount):
#        print(get_key(render_model.renderModelMarkerGroup.nameHash[x], render_model.nameHashDict))
#        for y in range(render_model.renderModelMarkerGroup.renderModelMarker[x].markerCount):
#            marker = render_model.renderModelMarkerGroup.renderModelMarker[x].marker[y]
#            
#            bpy.ops.mesh.primitive_uv_sphere_add(
#                radius = marker.scl / 10,
#                location = marker.pos
#            )
##            sphere_obj = bpy.data.objects.new("sphere_obj", bpy.data.armatures.new("sphere_obj"))
			
	
	##################################################################
	# Model
	##################################################################
	for x in range(render_model.renderModelRegion.regionCount): #render_model.renderModelRegion.regionCount
		regionName = get_key(render_model.renderModelRegion.nameHash[x], render_model.nameHashDict)
		
		regionCollection = bpy.data.collections.new(regionName)             #create collection within blender
		bpy.context.scene.collection.children.link(regionCollection)        #add collection to scene
		
		print(regionName)
		for y in range(render_model.renderModelRegion.renderModelPermutation[x].permutationCount):
			permutation = render_model.renderModelRegion.renderModelPermutation[x].permutation[y]
			permutationName = get_key(permutation.nameHash, render_model.nameHashDict)
			
			#print(" {0:4d} {1:4d} ".format(permutation.meshIndex, permutation.meshCount) + permutationName)
			for z in range(permutation.meshIndex, permutation.meshIndex + permutation.meshCount):
				lodRenderData = render_model.globalMesh.lodRenderData[z]
				#print("{0} {1}".format(lodRenderData.vertexBufferIndex[0], lodRenderData.indexBufferIndex))

				filePath2 = ""
				if render_model.renderModel.meshResourcePackingPolicy == 0:     #all meshes in one resource file
					filePath2 = filePath + "[" + str(0) + "_mesh resource!_]"
				if render_model.renderModel.meshResourcePackingPolicy == 1:     #meshes divided in between multiple resource files
					groupLookup = render_model.meshResourceGroupLookUp.meshResourceGroupLookUp[lodRenderData.vertexBufferIndex[0]]
					filePath2 = filePath + "[" + str(groupLookup.resourceGroupIndex) + "_mesh resource!_]"
				
				if os.path.exists(filePath2):
					#print("Loading mesh resource: {0}".format(filePath2))
					h = open(filePath2, "rb")
					render_model_resource = modelFile(h)

					vertexOffset = 0
					indexOffset = 0
					bufferIndex = 0
					if render_model.renderModel.meshResourcePackingPolicy == 0:
						vertexOffsetTable = render_model_resource.table4Array[lodRenderData.vertexBufferIndex[0]]                #todo change it so it dosent guess the index
						indexOffsetTable = render_model_resource.table4Array[lodRenderData.indexBufferIndex + render_model_resource.vertexBuffers.vertexBuffersCount]

						vertexOffset = render_model_resource.table2Array[vertexOffsetTable.table2ID].offset + render_model_resource.resourceOffset
						indexOffset = render_model_resource.table2Array[indexOffsetTable.table2ID].offset + render_model_resource.resourceOffset

						bufferIndex = lodRenderData.vertexBufferIndex[0]

					if render_model.renderModel.meshResourcePackingPolicy == 1:
						groupLookup = render_model.meshResourceGroupLookUp.meshResourceGroupLookUp[lodRenderData.vertexBufferIndex[0]]

						vertexOffsetTable = render_model_resource.table4Array[groupLookup.groupItemIndex]                #todo change it so it dosent guess the index
						indexOffsetTable = render_model_resource.table4Array[groupLookup.groupItemIndex + render_model_resource.vertexBuffers.vertexBuffersCount]

						vertexOffset = render_model_resource.table2Array[vertexOffsetTable.table2ID].offset + render_model_resource.resourceOffset
						indexOffset = render_model_resource.table2Array[indexOffsetTable.table2ID].offset + render_model_resource.resourceOffset

						bufferIndex = groupLookup.groupItemIndex


					print("{0:2x} {1:2x} {2:2x} {3:2x}".format(lodRenderData.vertexType, render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].declarationType, render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride, lodRenderData.rigidNodeIndex))
					
					vertexList = []
					uvList = []
					normalList = []
					nodeWeightAList = []
					nodeWeightBList = []
					nodeIndexAList = []
					nodeIndexBList = []
					
					h.seek(vertexOffset)
					if render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride == 0x18:
						for z in range(render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].count):
							vx = read_ushort(h) / 65535 * boundPosScale[0] + render_model.compressionInfo.compressionInfo[0].position_bounds_x0
							vy = read_ushort(h) / 65535 * boundPosScale[1] + render_model.compressionInfo.compressionInfo[0].position_bounds_y0
							vz = read_ushort(h) / 65535 * boundPosScale[2] + render_model.compressionInfo.compressionInfo[0].position_bounds_z0
							vw = read_ushort(h) / 65535 #null
							tu = read_ushort(h) / 65535 * boundUVScale[0] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0
							tv = read_ushort(h) / 65535 * boundUVScale[1] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0
						
							n1 = read_udec4n_2(h)
							b1 = read_uint(h)
							ukw = read_byte(h)          #colors?
							ukw2 = read_byte(h)
							ukw3 = read_byte(h)
							ukw4 = read_byte(h)
							
							vertexList.append((vx,vy,vz)*modelScale)
							uvList.append(Vector([tu,1-tv]))
							normalList.append(n1)
					if render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride == 0x1c:
						for z in range(render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].count):
							# if z < 100:
							# 	read_fixed_byte_string(h, 0x1c, 1, 1)
							vx = read_ushort(h) / 65535 * boundPosScale[0] + render_model.compressionInfo.compressionInfo[0].position_bounds_x0
							vy = read_ushort(h) / 65535 * boundPosScale[1] + render_model.compressionInfo.compressionInfo[0].position_bounds_y0
							vz = read_ushort(h) / 65535 * boundPosScale[2] + render_model.compressionInfo.compressionInfo[0].position_bounds_z0
							vw = read_ushort(h) / 65535 #null
							tu = read_ushort(h) / 65535 * boundUVScale[0] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0
							tv = read_ushort(h) / 65535 * boundUVScale[1] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0
							
							n1 = read_udec4n_2(h)
							b1 = read_uint(h)
							
							ia1 = read_byte(h)
							ia2 = read_byte(h)
							ia3 = read_byte(h)
							ia4 = read_byte(h)
							ukw = read_byte(h)
							ukw2 = read_byte(h)
							ukw3 = read_byte(h)
							ukw4 = read_byte(h)
							
							vertexList.append((vx,vy,vz)*modelScale)
							uvList.append(Vector([tu,1-tv]))
							#normalList.append(n1)
					if render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride == 0x20:
						for z in range(render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].count):
							# if z < 50:
							# 	read_fixed_byte_string(h, 0x20, 1, 1)
							vx = read_ushort(h) / 65535 * boundPosScale[0] + render_model.compressionInfo.compressionInfo[0].position_bounds_x0
							vy = read_ushort(h) / 65535 * boundPosScale[1] + render_model.compressionInfo.compressionInfo[0].position_bounds_y0
							vz = read_ushort(h) / 65535 * boundPosScale[2] + render_model.compressionInfo.compressionInfo[0].position_bounds_z0
							vw = read_ushort(h) / 65535 #null
							tu = read_ushort(h) / 65535 * boundUVScale[0] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0
							tv = read_ushort(h) / 65535 * boundUVScale[1] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0
							n1 = read_udec4n_2(h)
							b1 = read_uint(h)
							ia1 = read_byte(h)
							ia2 = read_byte(h)
							ia3 = read_byte(h)
							ia4 = read_byte(h)
							ukw = read_byte(h)
							ukw2 = read_byte(h)
							ukw3 = read_byte(h)
							ukw4 = read_byte(h)
							wa1 = read_byte(h) / 255
							wa2 = read_byte(h) / 255
							wa3 = read_byte(h) / 255
							wa4 = read_byte(h) / 255
							
							vertexList.append((vx,vy,vz)*modelScale)
							uvList.append(Vector([tu,1-tv]))
							normalList.append(n1)
							nodeIndexAList.append(Vector([ia1,ia2,ia3,ia4]))
							nodeWeightAList.append(Vector([wa1,wa2,wa3,wa4]))
					if render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride == 0x24:
						# print(str(lodRenderData.useDualQuat))
						for z in range(render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].count):
							# if z < 50:
							#     read_fixed_byte_string(h, 0x24, 1, 1)
							
							vx = read_ushort(h) / 65535 * boundPosScale[0] + render_model.compressionInfo.compressionInfo[0].position_bounds_x0
							vy = read_ushort(h) / 65535 * boundPosScale[1] + render_model.compressionInfo.compressionInfo[0].position_bounds_y0
							vz = read_ushort(h) / 65535 * boundPosScale[2] + render_model.compressionInfo.compressionInfo[0].position_bounds_z0
							vw = read_ushort(h) / 65535 #null
							tu = read_ushort(h) / 65535 * boundUVScale[0] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0
							tv = read_ushort(h) / 65535 * boundUVScale[1] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0
							n1 = read_udec4n_2(h)
							b1 = read_uint(h)
							ia4 = read_byte(h)
							ia3 = read_byte(h)
							ia2 = read_byte(h)
							ia1 = read_byte(h)
							wa4 = read_byte(h) / 255
							wa3 = read_byte(h) / 255
							wa2 = read_byte(h) / 255
							wa1 = read_byte(h) / 255
							ukw = read_byte(h)
							ukw2 = read_byte(h)
							ukw3 = read_byte(h)
							ukw4 = read_byte(h)
							ukw5 = read_float(h)

							if wa1 == 0 and wa2 == 0 and wa3 == 0 and wa4 == 0:
								wa1 = 0.25
								wa2 = 0.25
								wa3 = 0.25
								wa4 = 0.25
							
							vertexList.append((vx,vy,vz)*modelScale)
							uvList.append(Vector([tu,1-tv]))
							normalList.append(n1)
							nodeIndexAList.append(Vector([ia1,ia2,ia3,ia4]))
							nodeWeightAList.append(Vector([wa1,wa2,wa3,wa4]))		
					if render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride == 0x2c:
						for z in range(render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].count):
							# if z < 50:
							# 	read_fixed_byte_string(h, 0x2c, 1, 1)
							
							vx = read_ushort(h) / 65535 * boundPosScale[0] + render_model.compressionInfo.compressionInfo[0].position_bounds_x0
							vy = read_ushort(h) / 65535 * boundPosScale[1] + render_model.compressionInfo.compressionInfo[0].position_bounds_y0
							vz = read_ushort(h) / 65535 * boundPosScale[2] + render_model.compressionInfo.compressionInfo[0].position_bounds_z0
							vw = read_ushort(h) / 65535 #null
							tu = read_ushort(h) / 65535 * boundUVScale[0] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_u0
							tv = read_ushort(h) / 65535 * boundUVScale[1] + render_model.compressionInfo.compressionInfo[0].texcoord_bounds_v0
							n1 = read_udec4n_2(h)
							b1 = read_uint(h)
							ia4 = read_byte(h)
							ia3 = read_byte(h)
							ia2 = read_byte(h)
							ia1 = read_byte(h)
							ib4 = read_byte(h)
							ib3 = read_byte(h)
							ib2 = read_byte(h)
							ib1 = read_byte(h)
							wa4 = read_byte(h) / 255
							wb4 = read_byte(h) / 255
							wa3 = read_byte(h) / 255
							wb3 = read_byte(h) / 255
							wa2 = read_byte(h) / 255
							wb2 = read_byte(h) / 255
							wa1 = read_byte(h) / 255
							wb1 = read_byte(h) / 255
							ukw = read_byte(h)
							ukw2 = read_byte(h)
							ukw3 = read_byte(h)
							ukw4 = read_byte(h)
							ukw5 = read_byte(h)
							ukw6 = read_byte(h)
							ukw7 = read_byte(h)
							ukw8 = read_byte(h)
							
							vertexList.append((vx,vy,vz)*modelScale)
							uvList.append(Vector([tu,1-tv]))
							normalList.append(n1)
							nodeIndexAList.append(Vector([ia1,ia2,ia3,ia4]))
                           #nodeIndexBList.append(Vector([ib1,ib2,ib3,ib4]))
							nodeWeightAList.append(Vector([wa1,wa2,wa3,wa4]))
                           #nodeWeightAList.append(Vector([wb1,wb2,wb3,wb4]))
					   
					indexList = []
					h.seek(indexOffset)
					if (render_model_resource.indexBuffers.indexBuffers[bufferIndex].stride == 2):
						for z in range(render_model_resource.indexBuffers.indexBuffers[bufferIndex].count // 3):
							fa = read_ushort(h)
							fb = read_ushort(h)
							fc = read_ushort(h)
							indexList.append([fa,fb,fc])
					if (render_model_resource.indexBuffers.indexBuffers[bufferIndex].stride == 4):
						for z in range(render_model_resource.indexBuffers.indexBuffers[bufferIndex].count // 3):
							fa = read_uint(h)
							fb = read_uint(h)
							fc = read_uint(h)
							indexList.append([fa,fb,fc])
					
					if lodRenderData.lodFlags == 1:
						new_mesh = bpy.data.meshes.new(permutationName)
						new_mesh.from_pydata(vertexList, [], indexList)
						new_mesh.use_auto_smooth = True
						
						new_mesh.uv_layers.new()
						uv_layer = new_mesh.uv_layers.active.data
						
						for loop in new_mesh.loops:
							uv_layer[loop.index].uv = uvList[loop.vertex_index]
						new_mesh.normals_split_custom_set_from_vertices([normalize_tuple(n) for n in normalList])
						
						# normals = []
						# for poly in new_mesh.polygons:
						# 	poly.use_smooth = True
						# 	for loop_index in poly.loop_indices:
						# 		uv_layer[loop_index].uv = uvList[new_mesh.loops[loop_index].vertex_index]
						# 		normals.append(normalList[new_mesh.loops[loop_index].vertex_index])
						# new_mesh.normals_split_custom_set(normals)
						
						
						
						new_mesh.update()
						mesh_obj = bpy.data.objects.new((str(hex(render_model_resource.vertexBuffers.vertexBuffers[bufferIndex].stride))), new_mesh)
						#mesh_obj = bpy.data.objects.new(permutationName, new_mesh)
						mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
						mod.object = armature_obj
						
#                        for x in range(render_model.renderModelNode.nodeCount):
#                            print("    "+armature_obj.data.bones[x].name)
#                        
						for node in armature_obj.data.bones:
							mesh_obj.vertex_groups.new(name = node.name)
						
						#parenting the bones throws the hierachy out of whack outside of edit mode, thanks blender
						if (lodRenderData.rigidNodeIndex != 0xff):
							for i in range(len(new_mesh.vertices)):
								mesh_obj.vertex_groups[armature_obj.data.bones.find(get_key(render_model.renderModelNode.nodeList[lodRenderData.rigidNodeIndex].nodeNameHash, render_model.nameHashDict))].add([i], 1.0, 'ADD')
						else:
							for i in range(len(nodeIndexAList)): #per vertex
								indices = nodeIndexAList[i]
								weights = nodeWeightAList[i]
								for j in range(len(weights)): # 1 through 4
									if weights[j] == 0:
										continue
									mesh_obj.vertex_groups[armature_obj.data.bones.find(get_key(render_model.renderModelNode.nodeList[int(indices[j])].nodeNameHash, render_model.nameHashDict))].add([i], weights[j], 'ADD')
								   
											
						regionCollection.objects.link(mesh_obj)
					   
					h.close()
					del h

	print("Last read @ {0:x}".format(tell(f)))

clean_scene()
os.system("cls")

#filePath = "D:/models/ripped/halo 5/characters/spartan_buck/spartan_buck.render_model"
filePath = "D:/models/ripped/halo 5/characters/spartan_masterchief/spartan_masterchief.render_model"
#filePath = "D:/models/ripped/halo 5/characters/spartan_locke/spartan_locke.render_model"
#filePath = "D:/models/ripped/halo 5/characters/spartan_palmer/spartan_palmer.render_model"
#filePath = "D:/models/ripped/halo 5/characters/spartan_tanaka/spartan_tanaka.render_model"
#filePath = r"D:\models\ripped\halo 5\characters\spartan_vale\spartan_vale.render_model"
#filePath = "D:/models/ripped/halo 5/characters/spartans/spartans.render_model"
#filePath = "D:/models/ripped/halo 5/characters/roland/roland.render_model"
#filePath = r"D:\models\ripped\halo 5\characters\lasky\lasky.render_model"
#filePath = "D:/models/ripped/halo 5/characters/elite/elite.render_model"
# filePath = "D:/models/ripped/halo 5/characters/arbiter/arbiter.render_model"
#filePath = "D:/models/ripped/halo 5/characters/hunter/hunter.render_model"
#filePath = "D:/models/ripped/halo 5/characters/grunt/grunt.render_model"
#filePath = r"D:\models\ripped\halo 5\characters\jackal\jackal.render_model"
#filePath = r"D:\models\ripped\halo 5\characters\halsey\halsey.render_model"
#filePath = r"D:\models\ripped\halo 5\characters\guardian_bird_hero\guardian_bird_hero.render_model"
#filePath = r"D:\models\ripped\halo 5\characters\mantis\mantis.render_model"
#filePath = r"E:\DUMP\deploy\any\levels\globals-rtx-1\levels\forge\assets\fo_block_simple_2x2x2_a\fo_block_simple_2x2x2_a.render_model"
#filePath = r"E:\DUMP\deploy\any\levels\globals-rtx-1\levels\forge\assets\fo_block_simple_2x2x4_a\fo_block_simple_2x2x4_a.render_model"
#filePath = r"D:\models\ripped\halo 5\weapons\pistol\boltshot\boltshot.render_model"
importModel(filePath)

#print(hex(mmh3.hash("no_geo",signed=False)))
#print(uuid.uuid5(uuid.NAMESPACE_DNS, 'RenderModelClothDataBlock'))