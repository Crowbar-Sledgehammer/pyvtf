from sys import exit
from os import path
from os import makedirs
from PIL import Image
from textwrap import dedent
from platform import system

import sys
import subprocess

from pprint import pprint

class skybox(object):
	"""docstring for skybox"""

	platform = {
		'Linux': {
			'steamdir': path.expanduser('~/.steam/steam/'),
			'steamcommon': path.expanduser('~/.steam/steam/SteamApps/common/'),
		},
		'Windows': {
			'steamdir': path.realpath('/Program Files (x86)/Steam/'),
			'steamcommon': path.realpath(
				'/Program Files (x86)/Steam/SteamApps/common/'
			),
		},
	}

	def __init__(this, inputfile=None, crop_map='sdklegacy'):

		# Valve binaries path
		this.path = path.realpath(
			'%(steamcommon)s/Team Fortress 2/bin/'
			% this.platform[system()]
		)
		# Suitable game folder ./materialsrc/pyvtf
		# This seems to let vavle binaries gind gameinfo.txt
		this.materialsrc = path.realpath(
			'%(steamcommon)s/Team Fortress 2/tf/materialsrc/pyvtf'
			% this.platform[system()]
		)

		this.uniquedir   = 'dev' #todo generate a unique path for eash runtime,
		                         #     part of safe parrallelization.
		super(skybox, this).__init__()

		this.crop(inputfile, crop_map)

	# Allowed Files sizes, this may be changed to logic later, basically:
	# - be organized into a grid of four columns and three rows
	# - every cell must be homogenous and square.
	# - cvery cell demention must be equal and a power of two.
	#
	# Possible Logic:
	#   Height must be = 2*n * 4
	#   Width  must be = 3/4 * HEIGHT
	crop_allowed_sizes = [
		(2048, 1536),
	]

	# Crop-maps
	crop_maps = {
		# Current Skybox Template as of 2014-31-05
		# https://developer.valvesoftware.com/wiki/File:Skybox_Template.jpg
		'sdk': {
			'LF': (  0, 1/3, 1/4, 2/3),
			'BK': (1/4, 1/3, 1/2, 2/3),
			'RT': (2/4, 1/3, 3/2, 2/3),
			'FT': (3/4, 1/3,   1, 2/3),
			'DN': (3/4, 2/3,   1,   1),
			'UP': (3/4,   0,   1, 1/3),
		},
		# See @sdk link, this is an older revision of the same file.
		#
		# https://developer.valvesoftware.com
		# /w/images/archive/7/75/20091216021014%21Skybox_Template.jpg
		'sdklegacy': {
			'BK': (  0, 1/3, 1/4, 2/3),
			'DN': (1/4, 2/3, 2/4,   1),
			'FT': (1/2, 1/3, 3/4, 2/3),
			'LF': (3/4, 1/3,   1, 2/3),
			'RT': (1/4, 1/3, 1/2, 2/3),
			'UP': (1/4,   0, 2/4, 1/3),
		},
	}

	#TODO Split vtf/vmt definition writing intot the compile function.

	# Skybox compile options
	skybox_vtf_txt = dedent('''
		nocompress 1;
		skybox 1;
		nomip 1;
		clamps 1;
		clampt 1;
		border 0;
	'''[1:-1])

	# skybox shaders
	skybox_vmt = dedent('''
		unlitgeneric
		{
			$basetexture "<VTF>"
			$hdrcompressedtexture "<VTF>"
			$nofog 1
			$ignorez 1
		}
	'''[1:-1])

	#TODO: Document Input.
	#TODO: Document definitions for extensions.
	def crop(this, skybox_file, crop_map):
		skybox_map = Image.open(skybox_file)

		width  = skybox_map.size[0]
		height = skybox_map.size[1]

		if not skybox_map.size in this.crop_allowed_sizes:
			print('image size not supported. allowed sizes:')
			pprint(this.crop_allowed_sizes)
			exit()

		if not width/4*3 == height:
			print('image is not 4:3 aspect ratio.')
			exit()

		this.workingdir = path.realpath(path.join(this.materialsrc, this.uniquedir))
		makedirs(this.workingdir, exist_ok=True)

		tga_files = []

		for suffix, crop in this.crop_maps[crop_map].items():
			filesplit   = path.splitext(skybox_file)
			skybox_face = skybox_map.copy()

			file_tga = filesplit[0] + suffix + '.tga'

			file_tga = path.join(this.workingdir, file_tga)

			# Expand crop fractions to pixel counts.
			crop_to = tuple([int(a*b) for a,b in zip(
				crop,
				(width, height, width, height)
			)])

			skybox_face.crop(crop_to).save(file_tga, quality=100)

			file_vtf_txt = filesplit[0] + suffix + '.txt'
			file_vtf_txt = path.join(this.workingdir, file_vtf_txt)
			with open(file_vtf_txt, 'w') as file_vtf_txt_fh:
				file_vtf_txt_fh.write(this.skybox_vtf_txt)

			file_vmt = filesplit[0] + suffix + '.vmt'
			file_vmt = path.join(this.workingdir, file_vmt)
			with open(file_vmt, 'w') as file_vmt_fh:
				file_vmt_fh.write(this.skybox_vmt)

			tga_files.append(file_tga)

			this.compile_vtf(file_tga)

	# vtex binary name
	vtex = 'vtex'

	def compile_vtf(this, file_tga):

		vtex_shell = subprocess.call(
			[
				path.realpath(path.join(this.path, this.vtex)),
				"-nopause",
				# "-mkdir",
				"-outdir",
				this.workingdir,
				file_tga
			],
			# stdout=subprocess.PIPE,
			# stderr=subprocess.PIPE,
			# shell=True,
			# cwd=this.workingdir
		)
