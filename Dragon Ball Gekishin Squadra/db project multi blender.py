import io
import sys
import math
import struct
# import uuid
import os
import bpy
import mathutils
from mathutils import Matrix, Quaternion, Vector
import bmesh
from array import array

def clean_scene():  	#stolen
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
	print ("Here at:	{0:x}".format(tell(file_object)))
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
def get_bit_at_index(number, index):
	return (number >> index) & 1
def print_list_as_string(lst, max_elements, format=0, to_print=0):
	"""
	Prints the elements of a list as a single string, stopping after max_elements.
	Allows formatting as either decimal or hexadecimal.

	Parameters:
	lst (list): The list of elements to print.
	max_elements (int): The maximum number of elements to include in the string.
	format (str): The format of the numbers ('decimal' or 'hexadecimal').
	"""
	if format == 0:
		result = ' '.join(map(str, lst[:max_elements]))
	elif format == 1:
		result = ' '.join(f"{x:8x}" if isinstance(x, int) else str(x) for x in lst[:max_elements])
	else:
		raise ValueError("Invalid format. Use 'decimal' or 'hexadecimal'.")

	if to_print == 1:
		print(result)
	return(result)
def get_file_name(file_path):
	return os.path.basename(file_path)
def assign_uvs(mesh, custom_uvs, uv_name):
	uv_layer = mesh.uv_layers.new(name=uv_name)
	for face in mesh.polygons:
		for loop_index in face.loop_indices:
			uv_coord = custom_uvs[face.vertices[loop_index % len(custom_uvs)]]
			uv_layer.data[loop_index].uv = uv_coord
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
def is_normalized(t, tolerance=1e-6):
	"""
	Checks if a tuple is normalized (i.e., its magnitude is 1.0).

	:param t: The tuple to check (e.g., (x, y, z) or (r, g, b, a)).
	:param tolerance: The tolerance within which the magnitude is considered to be 1.0.
	:return: True if the tuple is normalized, False otherwise.
	"""
	magnitude = math.sqrt(sum(component ** 2 for component in t))
	return abs(magnitude - 1.0) <= tolerance
clean_scene()
os.system("cls")

def importSkeleton(filePath):
	with open(filePath, 'rb') as f:
		skel = read_fixed_string(f, 4)
		fileSize = read_uint(f)
		unk = read_uint(f)
		null = read_uint(f)

		tableCount = read_ushort(f)
		unkCount = read_ushort(f)
		unkCount2 = read_ushort(f)
		unkCount3 = read_ushort(f)
		tableOffset = read_uint(f)
		boneIdOffset = read_uint(f)
		boneNameBufferOffset = read_uint(f)
		unk8 = read_ushort(f)
		unk9 = read_ushort(f)
		unk10 = read_ushort(f)
		motionSkelIndex = read_ushort(f)		# index of skeleton used for skinning and motion
		boneCount = read_uint(f)

		f.seek(boneIdOffset)
		boneIdList = [read_ushort(f) for x in range(boneCount)]

		armature_obj = bpy.data.objects.new("Armature", bpy.data.armatures.new("Armature")) 	# create armature object
		bpy.context.scene.collection.objects.link(armature_obj) 								# link armature object to scene
		bpy.context.view_layer.objects.active = armature_obj									# focus on armature object
		bpy.ops.object.mode_set(mode='EDIT')													# set scene to edit mode

		armature_obj.show_in_front = True
		# armature_obj.data.display_type = 'STICK'
		armature_obj.data.display_type = 'OCTAHEDRAL'

		# f.seek(tableOffset)
		# for x in range(tableCount):
		#   read_fixed_byte_string(f, 0x64, 0, 1)

		boneList = []
		parentIdList=[]
		for x in range(boneCount):
			f.seek(tableOffset + 0x64 * boneIdList[x])
			# read_fixed_byte_string(f, 0x64, 1, 0)

			boneNameHash = read_uint(f) 	# crc32
			unk = read_byte(f)  			# skelId?
			unk2 = read_byte(f) 			# skelParent?
			null = read_ushort(f)
			parentId = read_uint(f) - motionSkelIndex
			boneNameOffset = read_uint(f)
			read_fixed_byte_string(f, 0x24, 0, 0)   			# matrix
			read_fixed_byte_string(f, 0x30, 1, 0)   			# matrix 2
			m11 = read_float(f); m21 = read_float(f) ; m31 = read_float(f) ; m41 = read_float(f) 
			m12 = read_float(f); m22 = read_float(f) ; m32 = read_float(f) ; m42 = read_float(f) 
			m13 = read_float(f); m23 = read_float(f) ; m33 = read_float(f) ; m43 = read_float(f) 

			if x==0: parentId = -1
			parentIdList.append(parentId)

			boneName = ""
			if x < boneCount-1:
				boneName = getString(f, boneNameOffset + boneNameBufferOffset)
			else:
				boneName = str(x)   # last bone name is at the end of file which is corrupted

			#rot = Matrix(([m11, m12, m13],[m21, m22, m23],[m31, m32, m33]))
			rot = Matrix(([m11, m21, m31],[m12, m22, m32],[m13, m23, m33]))
			pos = Vector([m41, m42, m43]) # change in the future, Vector truncates numbers after 4 digits past the decimal
			scl = Vector([1,1,1])

			bone = armature_obj.data.edit_bones.new(str(x))
			bone.use_connect = False
			bone.length = 0.05
			bone.name = boneName
			armature_obj.data.edit_bones.active = bone

			print(boneName)

			bone.matrix = Matrix.LocRotScale(pos,rot,scl)

			if parentIdList[x] > -1:
				bone.parent = boneList[parentIdList[x]]

			boneList.append(bone)

		# for x in range(boneCount):
		#   bone = boneList[x]
		#   children = bone.children

		#   if len(children) != 1:
		#   	print(f"Bone '{bone.name}' does not have exactly one child.")
		#   	continue

		#   child = children[-1]
		#   direction = (child.head - bone.head).normalized()
		#   length = (math.dist(bone.head, child.head)) / 2
		#   bone.tail = bone.head + direction * length


			# print(bone.name)
			# print(bone.parent.name)
			# print()

		# for node in armature_obj.data.edit_bones:
		#   print(node.name)

		bpy.ops.object.mode_set(mode = 'OBJECT')

		# for node in armature_obj.data.bones:
		#   print(node.name)

		print("Last read skeleton @ {0:x}".format(tell(f)))


def importModel(filePath):
	with open(filePath, 'rb') as f:
		fileName = get_file_name(filePath)

		mesh = read_fixed_string(f, 4)
		fileSize = read_uint(f)
		unk = read_uint(f)
		unk2 = read_uint(f)

		table1Count = read_ushort(f)
		table2Count = read_ushort(f)
		table3Count = read_ushort(f)
		table4Count = read_ushort(f)

		null = read_uint(f) 			# may be composed of two more table counts

		table1Offset = read_uint(f)
		table2Offset = read_uint(f)
		table3Offset = read_uint(f)
		table4Offset = read_uint(f)
		dataBaseOffset = read_uint(f)

		print("table1Count: {0:8x}  table1Offset: {1:8x}".format(table1Count, table1Offset))
		print("table2Count: {0:8x}  table2Offset: {1:8x}".format(table2Count, table2Offset))
		print("table3Count: {0:8x}  table3Offset: {1:8x}".format(table3Count, table3Offset))
		print("table4Count: {0:8x}  table4Offset: {1:8x}".format(table4Count, table4Offset))

		# f.seek(0x18, 1) 				# bound box
		for x in range(6):
			print(read_float(f))

		class _table1():
			def __init__(self):
				read_fixed_byte_string(f, 0x188, 1, 1)
				f.seek(0x10, 1) 				# floats?
				self.unk = read_uint(f) 		# index?
				self.unk2 = read_uint(f)		# index?
				f.seek(0x170, 1)				# mostly null but sometimes floats or other data
		class _table2():
			def __init__(self):
				# read_fixed_byte_string(f, 0x28, 1, 1)
				self.table1Id = read_ushort(f)
				self.table4Id = read_ushort(f)
				self.table3Id = read_uint(f)	#bodyBoneId?
				self.null = read_uint(f)
				self.indexCount = read_uint(f)
				self.boundMin = [read_float(f) for x in range(3)]
				self.boundMax = [read_float(f) for x in range(3)]
		class _table3():
			#new bone positions or bound boxes
			def __init__(self):
				read_fixed_byte_string(f, 0x1c, 1, 1)	
				self.boneId = read_uint(f)
				self.unkMin = [read_float(f) for x in range(3)]	# -0.5
				self.unkMax = [read_float(f) for x in range(3)]	# 0.5
		class _table4():
			def __init__(self):
				self.meshOffset = read_uint(f)
		
		modelCollection = bpy.data.collections.new(fileName)				# create collection within blender
		bpy.context.scene.collection.children.link(modelCollection) 

		f.seek(table1Offset)
		table1List = [_table1() for x in range(table1Count)]

		f.seek(table2Offset)
		table2List = [_table2() for x in range(table2Count)]

		f.seek(table3Offset)
		table3List = [_table3() for x in range(table3Count)]

		f.seek(table4Offset)
		table4List = [_table4() for x in range(table4Count)]


		for x in range(table2Count):	# table2Count
			table2 = table2List[x]
			table1 = table1List[table2.table1Id]
			table3 = table3List[table2.table3Id]
			table4 = table4List[table2.table4Id]
			
			meshOffset = table4.meshOffset

			f.seek(meshOffset)
			# read_fixed_byte_string(f, 0x24, 1, 1)
			morphsOffset = read_uint(f)
			vertexCount = read_uint(f)
			vertexLength = read_uint(f)
			vertexOffset = read_uint(f)
			vertexAttributes = read_ushort(f)
			primitiveType = read_ushort(f)
			indexCount = read_uint(f)
			indexLength = read_uint(f)
			indexOffset = read_uint(f)
			morphsFlag = read_ushort(f)   # sometimes 0x100

			print(str(x))
			print("vertexCount: {0:8x}  indexCount: 	{1:8x}".format(vertexCount, indexCount))
			print("vertexOffset:	{0:8x}  indexOffset:	{1:8x}".format(vertexOffset + meshOffset, indexOffset + meshOffset))

			positionsList = []
			normalsList = []
			colorsList = []
			uvList = [[],[],[],[]]
			weightsList = []
			boneIdsList = []
			indexList = []
			shapeKeyList = []

			modelScale = 1  # making this more than 1 removes vertices for some reason, thanks blender.

			f.seek(vertexOffset + meshOffset)
			for y in range(15):
				if (vertexAttributes >> y) & 1 == 1:
					match y:
						case 0:	# positions
							for z in range(vertexCount):
								vx = read_float(f)
								vy = read_float(f)
								vz = read_float(f)

								positionsList.append([vx,vy,vz])
						case 1: 	# normals
							for z in range(vertexCount):
								nx = (read_byte(f) / 127.5) - 1.0
								ny = (read_byte(f) / 127.5) - 1.0
								nz = (read_byte(f) / 127.5) - 1.0
								nw = (read_byte(f) / 127.5) - 1.0

								if z < 10:
									print([nx,ny,nz])
									print(repr(Vector([nx,ny,nz])))

								normalsList.append(Vector([nx,ny,nz]).normalized())
						case 2: 	# colors
							for z in range(vertexCount):
								cr = read_byte(f)
								cg = read_byte(f)
								cb = read_byte(f)
								ca = read_byte(f)
						case 3: 	# uv's 1 for solid colors?
							for z in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uvList[0].append(Vector([tu,1-tv]))
						case 4: 	# uv's 2 for diffuse?
							for z in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uvList[1].append(Vector([tu,1-tv]))
						case 5: 	# uv's 3 unknown
							for z in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uvList[2].append(Vector([tu,1-tv]))
						case 6: 	# uv's 4 unknown
							for z in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uvList[3].append(Vector([tu,1-tv]))
						case 9: 	# weights
							for z in range(vertexCount):
								weight1 = read_float(f)
								weight2 = read_float(f)
								weight3 = read_float(f)
								weight4 = read_float(f)

								weightsList.append([weight1,weight2,weight3,weight4])
						case 10: 	# bone id's
							for z in range(vertexCount):
								bone1 = read_byte(f)
								bone2 = read_byte(f)
								bone3 = read_byte(f)
								bone4 = read_byte(f)

								boneIdsList.append([bone1,bone2,bone3,bone4])
						case _:
							# 7/8 = tangent/bitangent
							print("unknown vertex attribute: {0}".format(y))

			f.seek(indexOffset + meshOffset)
			for y in range(indexCount // 3):
				fa = read_ushort(f)
				fb = read_ushort(f)
				fc = read_ushort(f)

				# end of files are sometimes corrupted
				if fa >= vertexCount or fb >= vertexCount or fc >= vertexCount: 
					fa = (vertexCount - 3)   
					fb = (vertexCount - 2)
					fc = (vertexCount - 1)

				indexList.append([fa,fb,fc])

			f.seek(morphsOffset + meshOffset)
			if morphsFlag == 0x100:
				shapeKeyCount = read_uint(f)
				shapeKeyDataLength = read_uint(f)
				shapeKeyBoundMin = [read_float(f) for y in range(3)]
				shapeKeyBoundMax = [read_float(f) for y in range(3)]
				shapeKeyNameHashList = [read_uint(f) for y in range(shapeKeyCount)]

				print("shapeKeyCount: {0:8}".format(shapeKeyCount))
				
				for y in range(shapeKeyCount):
					shapeKeyDeltaVertexList = [read_uint(f) for z in range(vertexCount)]	# packed / unknown encoding
					
					shapeKeyDeltaPositionsList = []
					for z, shapeKeyDeltaVertex in enumerate(shapeKeyDeltaVertexList):
						dx = (((shapeKeyDeltaVertex >> 0)  & 0x7FF) / 2047.0) * shapeKeyBoundMax[0] - shapeKeyBoundMin[0]
						dy = (((shapeKeyDeltaVertex >> 11) & 0x7FF) / 2047.0) * shapeKeyBoundMax[1] - shapeKeyBoundMin[1]
						dz = (((shapeKeyDeltaVertex >> 22) & 0x3FF) / 1023.0) * shapeKeyBoundMax[2] - shapeKeyBoundMin[2]

						shapeKeyDeltaPositionsList.append([dx,dy,dz])

					shapeKeyList.append(shapeKeyDeltaPositionsList)
			
			if x != 13000:
				meshName = str(x)

				new_mesh = bpy.data.meshes.new(meshName)
				new_mesh.from_pydata(positionsList, [], indexList)
				
				# new_mesh.update()

				new_mesh.polygons.foreach_set("use_smooth", [True] * len(new_mesh.polygons))
				new_mesh.update(calc_edges=True)
				new_mesh.normals_split_custom_set_from_vertices(normalsList)

				uvChannelCount = sum(1 for sublist in uvList if len(sublist) > 0)
				print("UV Channel Count: {0}".format(uvChannelCount))
				for y in range(uvChannelCount):
					uv_layer = new_mesh.uv_layers.new(name=f"UVMap_{y}")
					for loop in new_mesh.loops:
						vert_index = loop.vertex_index
						uv_layer.data[loop.index].uv = uvList[y][vert_index]

				new_mesh.update()

				mesh_obj = bpy.data.objects.new(meshName, new_mesh)
				armature_obj = bpy.context.scene.collection.objects[0]

				mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
				mod.object = armature_obj

				for node in armature_obj.data.bones:
					mesh_obj.vertex_groups.new(name = node.name)

				# for poly in new_mesh.polygons:
				#   poly.use_smooth = True

				if mesh_obj.data.shape_keys == None and len(shapeKeyList) > 0:
					mesh_obj.shape_key_add(name='Basis',from_mix=False)
					mesh_obj.data.shape_keys.use_relative = True

				for x in range(1, len(shapeKeyList)):
					mesh_obj.shape_key_add(name="Shape_" + str(x),from_mix=False)
					shape_key = mesh_obj.data.shape_keys.key_blocks[-1]

					for i in range(len(positionsList)):
						shape_key.data[i].co.x += shapeKeyList[x][i][0] - shapeKeyList[0][i][0]
						shape_key.data[i].co.y += shapeKeyList[x][i][1] - shapeKeyList[0][i][1]
						shape_key.data[i].co.z += shapeKeyList[x][i][2] - shapeKeyList[0][i][2]
					shape_key.value = 0.0

				for i in range(vertexCount): #per vertex
					bones = boneIdsList[i]
					weights = weightsList[i]
					for j in range(len(weights)): # 1 through 4
						if weights[j] == 0: continue
						mesh_obj.vertex_groups[int(bones[j])].add([i], weights[j], 'ADD')

				modelCollection.objects.link(mesh_obj)
			print("")

		print("Last read model @ {0:x}".format(tell(f)))

skelPath = r"D:\tools\JPKGReader-master\JPKGReader-master\JPKGReader\bin\Debug\net8.0\output\100.skel"
importSkeleton(skelPath)

modelPath = r"D:\tools\JPKGReader-master\JPKGReader-master\JPKGReader\bin\Debug\net8.0\output\99.mesh"
importModel(modelPath)