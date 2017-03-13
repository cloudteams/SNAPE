# coding=utf-8

"""
Original author: Copyright 2016, Massimo Santini <santini@di.unimi.it>
Modified by: Copyright (c) 2016, 2017 FZI Forschungszentrum Informatik am Karlsruher Institut für Technologie

This file is part of "GraphvizAnim".

"GraphvizAnim" is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

"GraphvizAnim" is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
"GraphvizAnim". If not, see <http://www.gnu.org/licenses/>.
"""

from subprocess import Popen, PIPE, STDOUT, call
import os
from config import image_magick_convert_path

def render( graphs, basename, fmt = 'png' , xdim = 10, ydim = 8):
	paths = []
	for n, graph in enumerate( graphs ):
		with open('temp_dot_file_%i.txt' % n, 'w') as stats_file:
			stats_file.write(graph)
		path = '{}_{:03}.{}'.format( basename, n, fmt )
		with open( path , 'w' ) as out:
			pipe = Popen( [ 'dot', '-T', fmt , '-Gsize=%i,%i\\!' % (xdim,ydim), '-Gdpi=100'], stdout = out, stdin = PIPE, stderr = None )
			pipe.communicate( input = graph )
		paths.append( path )
	return paths

def gif( files, basename, delay = 100 , xdim = 10, ydim = 8):
	for file in files:
		cmd = [image_magick_convert_path]
		cmd.extend( ( file, '-gravity', 'center', '-background', '#411F48', '-extent', '%i00x%i00' % (xdim,ydim), file ) )					#-background -> padding
		call( cmd )

	cmd = [image_magick_convert_path]
	for file in files:
		cmd.extend( ( '-delay', str( delay ), file ) )
	cmd.append( basename + '.gif' )
	call( cmd )
