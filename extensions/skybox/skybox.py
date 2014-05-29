from sys import exit
from os import path
from os import makedirs
from PIL import Image
from textwrap import dedent

import subprocess

from pprint import pprint

class skybox(object):
	"""docstring for skybox"""

	vtex        = 'vtex'
	hl2bins     = path.realpath('/Program Files (x86)/Steam/SteamApps/common/Team Fortress 2/bin/')
	materialsrc = path.realpath('/Program Files (x86)/Steam/SteamApps/common/Team Fortress 2/tf/materialsrc/pyvtf')
	uniquedir   = 'dev'

	allowed_sizes = [
		(2048, 1536),
	]

	skybox_vtf_txt = dedent('''
		nocompress 1;
		skybox;
		nomip 1;
		clamps 1;
		clampt 1;
		border 0;
	'''[1:-1])

	skybox_vmt = dedent('''
		unlitgeneric
		{
			$basetexture "<VTF>"
			$hdrcompressedtexture "<VTF>"
			$nofog 1
			$ignorez 1
		}
	'''[1:-1])

	# Crop-maps
	crops = {
		'BK': (  0, 1/3, 1/4, 2/3),
		'DN': (1/4, 2/3, 2/4,   1),
		'FT': (1/2, 1/3, 3/4, 2/3),
		'LF': (3/4, 1/3,   1, 2/3),
		'RT': (1/4, 1/3, 1/2, 2/3),
		'UP': (1/4,   0, 2/4, 1/3),
	}

	def __init__(this, inputfile=None):
		super(skybox, this).__init__()

		if None == inputfile:
			print("Missing file path to process")

		this.inputfile = inputfile
		skybox_map = Image.open(inputfile)
		width  = skybox_map.size[0]
		height = skybox_map.size[1]

		if not skybox_map.size in this.allowed_sizes:
			print('image size not supported. allowed sizes:')
			pprint(this.allowed_sizes)
			exit()

		if not width/4*3 == height:
			print('image is not 4:3 aspect ratio.')
			exit()

		makedirs(path.join(this.materialsrc, this.uniquedir), exist_ok=True)

		tga_files = []

		for suffix, crop in this.crops.items():
			filesplit   = path.splitext(inputfile)
			skybox_face = skybox_map.copy()

			file_tga = filesplit[0] + suffix + '.tga'

			file_tga = path.join(this.materialsrc, this.uniquedir, file_tga)

			crop_to = tuple([int(a*b) for a,b in zip(
				crop,
				(width, height, width, height)
			)])

			skybox_face.crop(crop_to).save(file_tga, quality=100)

			file_vtf_txt = filesplit[0] + suffix + '.txt'
			file_vtf_txt = path.join(this.materialsrc, this.uniquedir, file_vtf_txt)
			with open(file_vtf_txt, 'w') as file_vtf_txt_fh:
				file_vtf_txt_fh.write(this.skybox_vtf_txt)

			tga_files.append(file_tga)

		subprocess.call(
			[
				this.vtex,
				" -nopause",
				" -mkdir",
				" -outdir " + path.realpath(path.join(this.materialsrc, this.uniquedir))
			] + tga_files
		,	env={'PATH': path.realpath(this.hl2bins)},
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			shell=True,
			cwd=path.realpath(path.join(this.materialsrc, this.uniquedir))
		)
