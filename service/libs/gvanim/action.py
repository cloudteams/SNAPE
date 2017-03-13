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

import animation

def find_cluster_parent(id, root):
	for key in root:
		if key == id:
			return root
		else:
			for elem in root[key]:
				if isinstance(elem, dict):
					candidate = find_cluster_parent(id, elem)
					if candidate is not None:
						return candidate
	return None


class NextStep( object ):
	def __init__( self, clean = False ):
		self.clean = clean
	def __call__( self, steps ):
		steps.append( animation.Step( None if self.clean else steps[ -1 ] ) )

class AddNode( object ):
	def __init__( self, v , options):
		self.v = v
		self.options = options
	def __call__( self, steps ):
		steps[ -1 ].V.add( self.v )
		steps[ -1 ].Nopt[( self.v )] = self.options

class HighlightNode( object ):
	def __init__( self, v ):
		self.v = v
	def __call__( self, steps ):
		steps[ -1 ].V.add( self.v )
		steps[ -1 ].hV.add( self.v )

class LabelNode( object ):
	def __init__( self, v, label ):
		self.v = v
		self.label = label
	def __call__( self, steps ):
		steps[ -1 ].V.add( self.v )
		steps[ -1 ].L[ self.v ] = self.label

class UnlabelNode( object ):
	def __init__( self, v ):
		self.v = v
	def __call__( self, steps ):
		steps[ -1 ].V.add( self.v )
		del steps[ -1 ].L[ self.v ]

class RemoveNode( object ):
	def __init__( self, v ):
		self.v = v
	def __call__( self, steps ):
		steps[ -1 ].V.discard( self.v )
		steps[ -1 ].hV.discard( self.v )
		if self.v in steps[ -1 ].L: del steps[ -1 ].L[ self.v ]
		dE = set( e for e in steps[ -1 ].E if self.v in e )
		steps[ -1 ].E -= dE
		steps[ -1 ].hE -= dE

class AddEdge( object ):
	def __init__( self, u, v , options = None):
		self.u = u
		self.v = v
		self.options = options
	def __call__( self, steps ):
		steps[ -1 ].V.add( self.u )
		steps[ -1 ].V.add( self.v )
		steps[ -1 ].E.add( ( self.u, self.v ) )
		steps[ -1 ].Eopt[( self.u, self.v )] = self.options

class HighlightEdge( object ):
	def __init__( self, u, v ):
		self.u = u
		self.v = v
	def __call__( self, steps ):
		steps[ -1 ].V.add( self.u )
		steps[ -1 ].V.add( self.v )
		steps[ -1 ].E.add( ( self.u, self.v ) )
		steps[ -1 ].hE.add( ( self.u, self.v ) )

class RemoveEdge( object ):
	def __init__( self, u, v ):
		self.u = u
		self.v = v
	def __call__( self, steps ):
		steps[ -1 ].E.discard( ( self.u, self.v ) )
		steps[ -1 ].hE.discard( ( self.u, self.v ) )

class CreateCluster( object ):
	def __init__( self , cluster_id, parent_cluster_id ):
		self.cluster_id = cluster_id
		self.parent_cluster_id = parent_cluster_id
	def __call__( self, steps ):
		if find_cluster_parent(id = self.cluster_id, root = steps[-1].C) != None:
			return
		if self.parent_cluster_id is None:
			steps[ -1 ].C[ self.cluster_id ] = []
		else:
			grandparent = find_cluster_parent(id = self.parent_cluster_id, root = steps[-1].C)
			grandparent[self.parent_cluster_id].append( { self.cluster_id : [] } )

class NodeToCluster( object ):
	def __init__( self , cluster_id, node_id):
		self.cluster_id = cluster_id
		self.node_id = node_id
	def __call__( self, steps ):
		parent = find_cluster_parent(id = self.cluster_id, root = steps[-1].C)
		if parent is not None:
			parent[self.cluster_id].append( self.node_id )
		else:
			steps[ -1 ].C[ self.cluster_id ] = [ self.node_id ]

# do not use
class ClusterToCluster( object ):
	def __init__( self , cluster_id, new_cluster_id):
		self.cluster_id = cluster_id
		self.new_cluster_id = new_cluster_id
	def __call__( self, steps ):
		parent = find_cluster_parent(id = self.cluster_id, root = steps[-1].C)
		if parent is not None:
			parent[self.cluster_id].append( { self.new_cluster_id : [] } )

class MakeClusterVisible( object ):
	def __init__( self , cluster_id , highlight ):
		self.cluster_id = cluster_id
		self.hightlight = highlight
	def __call__(self, steps):
		steps[ -1 ].cV.add( self.cluster_id )
		if self.hightlight: steps[ -1 ].hC.add( self.cluster_id )

class MakeClusterInvisible( object ):
	def __init__( self , cluster_id ):
		self.cluster_id = cluster_id
	def __call__(self, steps):
		steps[ -1 ].cV.discard( self.cluster_id )
