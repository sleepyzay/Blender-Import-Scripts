import os
import io
import sys
import struct
import math
# https://github.com/SamuraiOndo/pylzss0
import lzss
# https://github.com/magical/nlzss
import lzss3
from glob import glob
from PIL import Image
import tkinter as tk
from tkinter import filedialog

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
def unpack_all_in_folder(directory):
	all_files = os.listdir(directory)
	for file_name in all_files:
		if file_name.split('.')[-1].lower() == 'amb':
			file_path = os.path.join(directory, file_name)
			unpack_amb(file_path)
def getString(file_object, stringOffset):
	backJump = tell(file_object)
	file_object.seek(stringOffset)
	s = read_string(file_object)
	file_object.seek(backJump)
	return s

from PIL import Image
import struct

def createImage(textureData, pixelData, paletteData, paletteIndex = 0):
	palette = []
	maxColors = (len(paletteData) // textureData.paletteCount) // 2

	# not always consistant, composure may be defined by flags yet to be found
	# 0 = diffuse
	# 1 = impact frame lighting
	# 2 = monotone
	# 3 = black except for the alpha pixels
	# 4 = alt diffuse
	# 5 = color highlight?

	print("paletteCount: {0:1x}".format(textureData.paletteCount))
	print("paletteSelected: {0:1x}".format(paletteIndex))
	print("maxColors: {0:1x}".format(maxColors))

	for i in range((maxColors * 2) * paletteIndex, (maxColors * 2) * paletteIndex + (maxColors * 2), 2):
		# Get 16-bit value from two bytes
		colorValue = struct.unpack("<H", paletteData[i:i+2])[0]
		
		# Extract r5g5b5 components
		r8 = ((colorValue >>  0) & 0x1F) * 255 // 31
		g8 = ((colorValue >>  5) & 0x1F) * 255 // 31
		b8 = ((colorValue >> 10) & 0x1F) * 255 // 31

		palette.append([r8, g8, b8])

	# Pad the palette to 256 entries if necessary
	while len(palette) < 256:
		palette.append((0, 0, 0))

	# print(textureData.bitsPerPixel)

	interpretedPixels = []
	if textureData.bitsPerPixel == 2:
		# 2bpp: Each byte represents four pixels, so unpack them
		# Is incorrectly reading the data?
		for byte in pixelData:
			# print("{0:08b}".format(byte))
			interpretedPixels.append((byte >> 0) & 0x03)
			interpretedPixels.append((byte >> 2) & 0x03)
			interpretedPixels.append((byte >> 4) & 0x03)
			interpretedPixels.append((byte >> 6) & 0x03)
	elif textureData.bitsPerPixel == 3:
		# 4bpp: Each byte represents two pixels, so we need to unpack them
		for byte in pixelData:
			interpretedPixels.append((byte >> 0) & 0x0F)
			interpretedPixels.append((byte >> 4) & 0x0F)
	elif textureData.bitsPerPixel == 4:
		# 8bpp: Each byte directly corresponds to a pixel index
		interpretedPixels = list(pixelData)
	
	rgba_pixels = []
	for pixelIndex in interpretedPixels:
		r8, g8, b8 = palette[pixelIndex]
		if [r8, g8, b8] == [0, 255, 0]:
			rgba_pixels.append((r8, g8, b8, 0))  # Transparent
			# rgba_pixels.append((0, 0, 0, 255))  # Black
		else:
			rgba_pixels.append((r8, g8, b8, 255))  # Opaque
			# rgba_pixels.append((255, 255, 255, 255))  # Black

	image = Image.new('RGBA', (textureData.textureWidth, textureData.textureHeight))
	image.putdata(rgba_pixels)
	return image

class _boneData():
	def __init__(self, f):
		self.matrix = [read_uint(f) / 4096.0 for x in range(12)]		
class _boneData2():
	def __init__(self, f):
		# read_fixed_byte_string(f, 0x14, 1, 1)
		self.unk = read_ushort(f)		# 0201
		self.unk2 = read_uint(f)		# offset?
		self.unk3 = read_ushort(f)		# 0001
		self.nameOffset = read_uint(f)	# geoshape / geol
		self.parentId = read_ushort(f)
		self.siblingId = read_ushort(f)
		self.offset = read_uint(f)
class _meshData():
	def __init__(self, f):
		# read_fixed_byte_string(f, 0x10, 1, 1)
		self.nameOffset = read_uint(f)
		self.offset = read_uint(f)
		self.unk = read_ushort(f)			# 0x60 / 0x61
		self.unk2 = read_byte(f)
		self.unk3 = read_byte(f)
		self.unk4 = read_ushort(f)
		self.scale = (2 ** read_ushort(f))
class _meshData2():
	def __init__(self, f):
		# read_fixed_byte_string(f, 0x10, 1, 1)
		self.nameOffset = read_uint(f)
		self.boneId = read_uint(f)
		self.index = read_uint(f)
		self.null = read_uint(f)
class _materialData():
	def __init__(self, f):
		# read_fixed_byte_string(f, 0x24, 1, 1)
		nameOffset = read_uint(f)
		f.seek(0x03, 1)							# 0F 03 1F
		unkId = read_byte(f)
		f.seek(0x08, 1)							# 39 67 00 00 00 00 E7 1C
		textureId = read_byte(f)
		f.seek(0x13, 1)							# FD 01 01 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00
class _textureData():
	def __init__(self, f):
		read_fixed_byte_string(f, 0x30, 1, 1)
		self.texturePathOffset = read_uint(f)
		self.pixelOffset = read_uint(f)
		self.pixelUncompressedLength = read_uint(f)
		self.pixelCompressedLength = read_ushort(f)
		self.pixelUnk = read_ushort(f)
		self.paletteOffset = read_uint(f)
		self.paletteLength = read_uint(f)
		self.textureWidth = read_ushort(f)
		self.textureHeight = read_ushort(f)
		self.null = read_uint(f)
		self.null2 = read_uint(f)
		self.bitsPerPixel = read_byte(f)		# 3 = 4 / 4 = 8
		self.unk2 = read_byte(f)
		self.unk3 = read_byte(f)
		self.paletteCount = read_byte(f)
		self.textureNameOffset = read_uint(f)	# textureName is substring of texturePath
		self.unk4 = read_byte(f)
		self.compressionType = read_byte(f)		# 0 = uncompressed? / 1 = lz10 / 2 = lzss0
		self.null3 = read_ushort(f)
class _seactionHeader():
		def __init__(self, f):
			self.offset = f.tell()
			self.type = read_byte(f)
			self.unk = read_byte(f)
			self.materialId = read_byte(f)
			self.boneMapCount = read_byte(f)
			self.length = read_uint(f)
			self.end = self.offset + self.length

def parseDse(f):
	magic = read_string(f)
	if magic != "DSE":
		print("Not DSE file, exiting script.")
		# sys.exit(1)  # Exit the script with an error status
		return

	f.seek(0x1e)
	unk = read_ushort(f)
	unk2 = read_ushort(f)
	boneCount = read_ushort(f)
	meshCount = read_ushort(f)
	meshCount2 = read_ushort(f)			# same as meshCount
	materialCount = read_ushort(f)
	textureCount = read_ushort(f)

	boneDataOffset = read_uint(f)
	boneDataOffset2 = read_uint(f)
	meshDataOffset = read_uint(f)
	meshDataOffset2 = read_uint(f)
	materialDataOffset = read_uint(f)
	textureDataOffset = read_uint(f)    # length?
	stringBufferOffset = read_uint(f)

	unkOffset = read_uint(f)			# another baseOffset? / null
	stringBufferOffset2 = read_uint(f)	# another baseOffset? / usually the same as stringBufferOffset
	stringBufferLength = read_uint(f)
	fileNameOffset = read_uint(f)		# relative to stringBufferOffset
	unkDataOffset = read_uint(f)
	textureBufferOffset = read_uint(f)
	fileSize = read_uint(f)

	baseOffset = tell(f)
	# print("boneCount: {0} meshCount: {1} materialCount: {2} textureCount: {3}".format(boneCount, meshCount, materialCount, textureCount))

	f.seek(boneDataOffset + baseOffset)
	boneDataList = [_boneData(f) for x in range(boneCount)]

	f.seek(boneDataOffset2 + baseOffset)
	boneDataList2 = [_boneData2(f) for x in range(boneCount)]

	f.seek(meshDataOffset + baseOffset)
	meshDataList = [_meshData(f) for x in range(meshCount)]

	f.seek(meshDataOffset2 + baseOffset)
	meshDataList2 = [_meshData2(f) for x in range(meshCount)]

	f.seek(materialDataOffset + baseOffset)
	materialDataList = [_materialData(f) for x in range(materialCount)]

	f.seek(textureDataOffset + baseOffset)
	textureDataList = [_textureData(f) for x in range(textureCount)]
	
	# print("textureBufferOffset: {0:x}".format(textureBufferOffset))

	for x, textureData in enumerate(textureDataList):
		if x != 20:
			f.seek(textureData.texturePathOffset + stringBufferOffset2 + baseOffset)
			texturePath = read_string(f)
			# print(texturePath)

			f.seek(textureData.textureNameOffset + stringBufferOffset2 + baseOffset)
			textureName = read_string(f)
			print(textureName)

			f.seek(textureData.paletteOffset + textureBufferOffset)
			paletteData = f.read(textureData.paletteLength)

			if textureData.bitsPerPixel == 2: print("bitsPerPixel: {0}".format(2))
			if textureData.bitsPerPixel == 3: print("bitsPerPixel: {0}".format(4))
			if textureData.bitsPerPixel == 4: print("bitsPerPixel: {0}".format(8))

			print("textureWidth: {0} textureHeight: {1}".format(textureData.textureWidth, textureData.textureHeight))

			print("paletteOffset: {0:x}".format(textureData.paletteOffset + textureBufferOffset))
			print("paletteLength: {0:x}".format(len(paletteData)))

			f.seek(textureData.pixelOffset + textureBufferOffset)

			print("pixelOffset: {0:x}".format(f.tell()))
			if textureData.compressionType == 0:
				print("uncompressed")
				# todo: add uncompressed texture support
				pixelData = f.read(textureData.pixelUncompressedLength)
			if textureData.compressionType == 1:
				print("compressed")
				compressedPixelData = f.read(textureData.pixelCompressedLength)
				pixelData = lzss3.decompress_bytes(compressedPixelData)
			if textureData.compressionType == 2:
				print("compressed")
				uncompressedLength = read_uint(f)
				compressedPixelData = f.read(textureData.pixelCompressedLength - (f.tell() - (textureData.pixelOffset + textureBufferOffset)))
				pixelData = lzss.decompress(compressedPixelData)

			# 	print("compressedLength:	{0:x}".format(len(compressedPixelData)))
			# 	print("decompressedLength:	{0:x}".format(len(pixelData)))
				

			# todo: add automatic multi palette export to designated folder
			# Create the image
			image = createImage(textureData, pixelData, paletteData)
			
			# Save or show the image
			# image.save(directory + "\\" + str(x) + ".png")
			image.save(os.path.dirname(f.name) + "\\" + textureName[:-4] + ".png")
			# image.show()
			# print(os.path.dirname(f.name))
			print()

				# output_file_path = "decompressed_output" + "_" + str(x) + ".binn"
				# print(output_file_path)
				# with open(output_file_path, "wb") as file:
				# 	file.write(decompressedPixelData)
				# 	file.write(paletteData)

	"""
	for x, (meshData, meshData2) in enumerate(zip(meshDataList, meshDataList2)):
		f.seek(meshData.offset + baseOffset)
		# print_here(f)

		while True:
			# print_here(f)
			section = _seactionHeader(f)
			if section.type == 0x02:
				pass
			if section.type == 0x03 or section.type == 0x04:
				vertexCount = read_ushort(f)
				vertexStride = read_byte(f)
				vertexFlags = read_byte(f)

				#		76543210
				# 19	00011001			tuv_h					vxyz_h w1-n_h
				# 1d	00011101			tuv_h	unk1_h			vxyz_h w1-n_h
				# 21	00100001	crgba_b							vxyz_h null_h
				# 25	00100101	crgba_b			unk1_h	unk2h	vxyz_h null_h
				# 29	00101001	crgba_b	tuv_h					vxyz_h null_h
				# 2d	00101101	crgba_b	tuv_h	unk1_h	unk2h	vxyz_h null_h
				#		76543210
				# unk1234: colors? / one vertex has this but no uv's
				# unk1:    looks like unk4 in meshData
				# unk2:    null / latter half of int?
				# 0: positions?
				# 1: 0
				# 2: unk1
				# 3: uv's?
				# 4: weights
				# 5: colors?
				# 6: 0
				# 7: 0

				print("{0:02x} {1:02x}".format(vertexStride, vertexFlags))

				f.seek(section.end)
			if section.type == 0x01:
				break
		# print()
	"""

	# print("Last read @ {0:x}".format(tell(f)))

# # directory = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr"
# # directory = r"D:\models\ripped\dbz nds\origins\root\character\DBMODEL"
# directory = r"D:\models\ripped\dbz nds\origins 2\root\New folder\archiveDB2\mdl\chr"
# all_files = [y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.dse'))]
# for filePath in all_files:
# 	print(filePath)
# 	f = open(filePath, "rb")
# 	parseDse(f)

root = tk.Tk()
root.withdraw()  # Hide the main window
filePath = filedialog.askopenfilename(title="Select a File", filetypes=(("DSE files", "*.dse"), ("All files", "*.*")))

# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\101100_goku\101100_goku.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\101103_goku_s3\101103_goku_s3.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\101110_goku_2p\101110_goku_2p.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\st\st_5000\st_5000.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\314600_dodoria.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\102100_bardock\102100_bardock.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\121130_vegeta_3p\121130_vegeta_3p.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\300100_near\300100_near.dse"
# # filePath = r"D:\models\ripped\dbz nds\ultimate butoden\archiveDBK.dsa\mdl\chr\New folder\302910_piccolo\302910_piccolo.dse"

directory = os.path.dirname(filePath)

f = open(filePath, "rb")
print(filePath)

parseDse(f)


