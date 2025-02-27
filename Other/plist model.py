import plistlib
import struct
import io
import sys
import math
import struct
import os
import bpy
import mathutils
import numpy

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

filePath = r""
clean_scene()

# Load plist file
with open(filePath, "rb") as file:
	plist_data = plistlib.load(file)

	for mesh in plist_data['mesh']:
		index_list = list(struct.iter_unpack("<HHH", mesh['index']))
		vertex_list = list(struct.iter_unpack("<fff", mesh['vertex']))
		uv_list = list(struct.iter_unpack("<ff", mesh['uv']))
		normal_list = list(struct.iter_unpack("<fff", mesh['normal']))
		mesh_name = mesh['name']
		
		new_mesh = bpy.data.meshes.new(mesh_name)
		new_mesh.from_pydata(vertex_list, [], index_list)

		# 4.1 and newer dosen't like this
		# new_mesh.use_auto_smooth = True

		new_mesh.uv_layers.new()
		uv_layer = new_mesh.uv_layers.active.data
		for loop in new_mesh.loops:
			uv_layer[loop.index].uv = uv_list[loop.vertex_index]

		mesh_obj = bpy.data.objects.new(mesh_name, new_mesh)

		bpy.context.collection.objects.link(mesh_obj)