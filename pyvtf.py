#!/c/Python34x32/python.exe

from sys import argv
from importlib import import_module

if '__main__' == __name__:

	if 2 > len(argv):
		print('main app here')

	else:
		module = import_module('extensions.' + argv[1] + '.' + argv[1])
		getattr(module, argv[1])(*argv[2:])
