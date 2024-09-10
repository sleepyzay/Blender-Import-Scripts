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

			pos = Vector([m41, m42, m43])
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

		f.seek(0x18, 1) 				# bound box

		class _table1():
			def __init__(self):
				# read_fixed_byte_string(f, 0x188, 1, 1)
				f.seek(0x10, 1) 				# floats?
				self.unk = read_uint(f) 		# index?
				self.unk2 = read_uint(f)		# index?
				f.seek(0x170, 1)				# mostly null but sometimes floats or other data
		class _table2():
			def __init__(self):
				# read_fixed_byte_string(f, 0x28, 1, 1)
				self.table1Id = read_ushort(f)
				self.table4Id = read_ushort(f)
				self.bodyBoneId = read_uint(f)  #table3Id?
				self.null = read_uint(f)
				self.indexCount = read_uint(f)
				self.unkFloat1 = read_float(f)
				self.unkFloat2 = read_float(f)
				self.unkFloat3 = read_float(f)
				self.unkFloat4 = read_float(f)
				self.unkFloat5 = read_float(f)
				self.unkFloat6 = read_float(f)
		class _table3():
			#new bone positions or bound boxes
			def __init__(self):
				# read_fixed_byte_string(f, 0x1c, 1, 1) 
				self.boneId = read_uint(f)
				self.unkFloat1 = read_float(f)
				self.unkFloat2 = read_float(f)
				self.unkFloat3 = read_float(f)
				self.unkFloat4 = read_float(f)
				self.unkFloat5 = read_float(f)
				self.unkFloat6 = read_float(f)
		class _table4():
			def __init__(self):
				self.meshOffset = read_uint(f)
				
		class mesh():
			def __init__(self, ):
				pass

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

		for x in range(table2Count):
			table2 = table2List[x]
			
			meshOffset = table4List[table2.table4Id].meshOffset

			f.seek(meshOffset)
			# read_fixed_byte_string(f, 0x24, 1, 1)
			meshLength = read_uint(f)
			vertexCount = read_uint(f)
			vertexLength = read_uint(f)
			vertexOffset = read_uint(f)
			vertexAttributes = read_ushort(f)
			primitiveType = read_ushort(f)
			indexCount = read_uint(f)
			indexLength = read_uint(f)
			indexOffset = read_uint(f)
			unk2 = read_ushort(f)   # sometimes 1
			unk3 = read_ushort(f)   # null?

			print("vertexCount: {0:8x}  indexCount: 	{1:8x}".format(vertexCount, indexCount))
			print("vertexOffset:	{0:8x}  indexOffset:	{1:8x}\n".format(vertexOffset + meshOffset, indexOffset + meshOffset))

			positionsList = []
			normalsList = []
			colorsList = []
			uv1List = []
			uv2List = []
			uv3List = []
			weightsList = []
			boneIdsList = []
			indexList = []

			modelScale = 1  # making this more than 1 removes vertices for some reason, thanks blender.

			f.seek(vertexOffset + meshOffset)
			for x in range(15, -1, -1):
				if (vertexAttributes >> x) & 1 == 1:
					match x:
						case 10:	# positions
							for y in range(vertexCount):
								vx = read_float(f)
								vy = read_float(f)
								vz = read_float(f)

								positionsList.append((vx,vy,vz)*modelScale)
						case 9: 	# normals
							for y in range(vertexCount):
								nx = ((read_byte(f) / 255.0) * 2) - 1
								ny = ((read_byte(f) / 255.0) * 2) - 1
								nz = ((read_byte(f) / 255.0) * 2) - 1
								nw = read_byte(f)

								normalsList.append((nx,ny,nz))
						case 5: 	# colors
							for y in range(vertexCount):
								ca = read_byte(f)
								cb = read_byte(f)
								cg = read_byte(f)
								cr = read_byte(f)
						case 4: 	# uv's 3
							for y in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uv3List.append(Vector([tu,1-tv]))
						case 3: 	# uv's 2
							for y in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uv2List.append(Vector([tu,1-tv]))
						case 2: 	# uv's 1
							for y in range(vertexCount):
								tu = read_half(f)
								tv = read_half(f)

								uv1List.append(Vector([tu,1-tv]))
						case 1: 	# weights
							for y in range(vertexCount):
								weight1 = read_float(f)
								weight2 = read_float(f)
								weight3 = read_float(f)
								weight4 = read_float(f)

								weightsList.append([weight1,weight2,weight3,weight4])
						case 0: 	# bone id's
							for y in range(vertexCount):
								bone1 = read_byte(f)
								bone2 = read_byte(f)
								bone3 = read_byte(f)
								bone4 = read_byte(f)

								boneIdsList.append([bone1,bone2,bone3,bone4])
						case _:
							print("unknown vertex attribute: {0}".format(x))

			f.seek(indexOffset + meshOffset)
			for x in range(indexCount // 3):
				fa = read_ushort(f)
				fb = read_ushort(f)
				fc = read_ushort(f)

				if fc >= vertexCount: fc = (vertexCount - 1)   # end of files are sometimes corrupted

				indexList.append([fa,fb,fc])

			meshName = str(x)

			# #BuildMesh
			# mesh1 = bpy.data.meshes.new("Mesh")
			# mesh1.use_auto_smooth = True
			# obj = bpy.data.objects.new(meshName,mesh1)
			# modelCollection.objects.link(obj)

			# bpy.context.view_layer.objects.active = obj
			# obj.select_set(True)

			# mesh = bpy.context.object.data
			# bm = bmesh.new()
			# for v in positionsList:
			#   bm.verts.new((v[0],v[1],v[2]))
			# list = [v for v in bm.verts]

			# for i in indexList:
			#   try:
			#   	bm.faces.new((list[i[0]],list[i[1]],list[i[2]]))
			#   except:
			#   	continue
					
			# bm.to_mesh(mesh)
			
			# uv_layer = bm.loops.layers.uv.verify()
			# Normals = []
			# for i in bm.faces:
			#   i.smooth=True
			#   for l in i.loops:
			#   	if normalsList != []:
			#   		Normals.append(normalsList[l.vert.index])
			#   	luv = l[uv_layer]
			#   	try:
			#   		luv.uv = uv1List[l.vert.index]
			#   	except:
			#   		continue
			# bm.to_mesh(mesh)

			# if normalsList != []:
			#   # mesh1.normals_split_custom_set(Normals)
			#   mesh1.normals_split_custom_set_from_vertices(normalsList)

			# my version
			uv0List = [Vector([0,0]) for x in range(vertexCount)]

			new_mesh = bpy.data.meshes.new(meshName)
			new_mesh.from_pydata(positionsList, [], indexList)
			new_mesh.use_auto_smooth = True

			new_mesh.update()

			new_mesh.uv_layers.new()
			uv_layer = new_mesh.uv_layers.active.data

			for loop in new_mesh.loops:
				uv_layer[loop.index].uv = uv0List[loop.vertex_index]
			new_mesh.normals_split_custom_set_from_vertices([normalize_tuple(n) for n in normalsList])
			#new_mesh.normals_split_custom_set_from_vertices(normalsList)
			
			# # Assign custom UV coordinates to each of the 3 UV channels
			# if len(uv1List) > 0: assign_uvs(new_mesh, uv1List, "UVMap_1")
			# if len(uv2List) > 0: assign_uvs(new_mesh, uv2List, "UVMap_2")
			# if len(uv3List) > 0: assign_uvs(new_mesh, uv3List, "UVMap_3")

			new_mesh.update()

			mesh_obj = bpy.data.objects.new(meshName, new_mesh)

			armature_obj = bpy.context.scene.collection.objects[0]
			# for node in armature_obj.data.bones:
			#   print(node.name)

			mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
			mod.object = armature_obj

			for node in armature_obj.data.bones:
				mesh_obj.vertex_groups.new(name = node.name)

			# for poly in new_mesh.polygons:
			#   poly.use_smooth = True

			for i in range(vertexCount): #per vertex
				bones = boneIdsList[i]
				weights = weightsList[i]
				for j in range(len(weights)): # 1 through 4
					if weights[j] == 0: continue
					mesh_obj.vertex_groups[int(bones[j])].add([i], weights[j], 'ADD')

			modelCollection.objects.link(mesh_obj)

		print("Last read model @ {0:x}".format(tell(f)))

skelPath = r"D:\models\ripped\db project multi\00000153.skel"
importSkeleton(skelPath)

modelPath = r"D:\models\ripped\db project multi\00000170.mesh"
importModel(modelPath)