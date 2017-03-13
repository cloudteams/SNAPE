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

from email.utils import quote
import shlex
from config import *

import action

class ParseException( Exception ):
    pass
class Step( object ):

    def __init__( self, step = None ):
        if False:
            self.V = step.V.copy()
            self.E = step.E.copy()
            self.L = step.L.copy()
            self.C = step.C.copy()
            self.Eopt = step.Eopt.copy()
            self.Nopt = step.Nopt.copy()
        else:
            self.V = set()
            self.E = set()
            self.L = dict()
            self.C = dict()
            self.Eopt = {}
            self.Nopt = {}
        self.hV = set()
        self.hE = set()
        self.cV = set()
        self.hC = set()

    def node_format( self, v , hide = False):
        fmt = []
        try:
            fmt.append( 'label={}'.format( ' ' + self.L[ v ].encode('utf-8') ) )
        except KeyError:
            pass
        if hide:
            fmt.append( 'style=invis' )
            if fmt: return '[{}]'.format( ','.join( fmt ) )
            return ''
        if v in self.Nopt and self.Nopt[v] is not None and (v in self.hV or v in self.V):
            if v in self.hV: return '[' + self.Nopt[v][:(len(self.Nopt[v]))] + ', color=%s, label=%s]' % (NODE_HIGHLIGHT_COLOR, self.L[v])
            else: return '[' + self.Nopt[v][:(len(self.Nopt[v]))] + ',color=%s, label=%s]' % (NODE_COLOR, self.L[v])
        if v in self.hV:
            fmt.append( 'color=%s' % NODE_HIGHLIGHT_COLOR)
        elif v not in self.V:
            fmt.append( 'style=invis' )
        else:
            fmt.append( 'color=%s' % NODE_COLOR)
        if fmt: return '[{}]'.format( ','.join( fmt ) )
        return ''

    def edge_format( self, e, hide = False ):
        if hide:
            return '[style=invis]'
        if e in self.Eopt and self.Eopt[e] is not None and (e in self.hE or e in self.E):
            if e in self.hE: return self.Eopt[e][:(len(self.Eopt[e])-1)] + ', color=%s]' % EDGE_HIGHLIGHT_COLOR
            else: return self.Eopt[e][:(len(self.Eopt[e])-1)] + ', color=%s]' % EDGE_COLOR
        if e in self.hE:
            return '[color=%s]' % EDGE_HIGHLIGHT_COLOR
        elif e in self.E:
            return ''
        return '[color=%s]' % EDGE_COLOR

    def __repr__( self ):
        return '{{ V = {}, E = {}, hV = {}, hE = {}, L = {}, Eopt = {}, Nopt = {} }}'.format( self.V, self.E, self.hV, self.hE, self.L, self.Eopt, self.Nopt )

class Animation( object ):

    def __init__( self ):
        self._actions = []

    def next_step( self, clean = False ):
        self._actions.append( action.NextStep( clean ) )

    def add_node( self, v , options = None):
        self._actions.append( action.AddNode( v, options ) )

    def highlight_node( self, v ):
        self._actions.append( action.HighlightNode( v ) )

    def label_node( self, v, label ):
        self._actions.append( action.LabelNode( v, label ) )

    def unlabel_node( self, v ):
        self._actions.append( action.UnlabelNode( v ) )

    def remove_node( self, v ):
        self._actions.append( action.RemoveNode( v ) )

    def add_edge( self, u, v , options = None):
        self._actions.append( action.AddEdge( u, v , options) )

    def highlight_edge( self, u, v ):
        self._actions.append( action.HighlightEdge( u, v ) )

    def remove_edge( self, u, v ):
        self._actions.append( action.RemoveEdge( u, v ) )

    def create_cluster( self , cluster_id, parent_cluster_id = None):
        self._actions.append( action.CreateCluster( cluster_id, parent_cluster_id ) )

    def add_node_to_cluster( self , cluster_id, node_id ):
        self._actions.append( action.NodeToCluster( cluster_id, node_id ) )

    def add_cluster_to_cluster( self , cluster_id, new_cluster_id ):
        self._actions.append( action.ClusterToCluster( cluster_id, new_cluster_id ) )

# do not use
    def make_cluster_visible( self , cluster_id , highlight = False):
        self._actions.append( action.MakeClusterVisible( cluster_id , highlight ) )

    def make_cluster_invisible( self , cluster_id ):
        self._actions.append( action.MakeClusterInvisible( cluster_id ) )

    def parse( self, lines ):
        action2method = {
            'ns' : self.next_step,
            'an' : self.add_node,
            'hn' : self.highlight_node,
            'ln' : self.label_node,
            'un' : self.unlabel_node,
            'rn' : self.remove_node,
            'ae' : self.add_edge,
            'he' : self.highlight_edge,
            're' : self.remove_edge,
        }
        for line in lines:
            parts = shlex.split( line.strip(), True )
            if not parts: continue
            action, params = parts[ 0 ], parts[ 1: ]
            try:
                action2method[ action ]( *params )
            except KeyError:
                raise ParseException( 'unrecognized command: {}'.format( action ) )
            except TypeError:
                raise ParseException( 'wrong number of parameters: {}'.format( line.strip() ) )

    def steps( self ):
        steps = [ Step() ]
        for action in self._actions:
            action( steps )
        return steps

    def graphs( self , use_cases, actors, uc_diagram):
        steps = self.steps()
        C, V, E = dict(), set(), set()
        for step in steps:
            C.update(step.C)
            V |= step.V
            E |= step.E
        graphs = []

        actors_first_half, actors_second_half = actors[:len(actors) / 2], actors[len(actors) / 2:]

        for n, s in enumerate( steps ):
            graph = ['digraph G {', 'fontpath="%s"' % font_path, 'fontname="%s"' % font_name, 'bgcolor=%s' %
                     BACKGROUND_COLOR,
                     'pad=".25"', 'ranksep=".75"', 'nodesep=".75"', 'rankdir="LR"' if uc_diagram else '',
                     'node[style=filled,fillcolor=%s,width=2,height=2,fontpath="%s",fontname="%s"]' %
                     (NODE_INSIDE_COLOR, font_path, font_name),
                     'edge[dir=back, arrowtail=vee, fontpath="%s", fontname="%s"]' % (font_path, font_name),
                     '{rank=min;%s}' % "".join(list(map(lambda x: '"%s";' % x, actors_first_half))),
                     '{rank=same;%s}' % "".join(list(map(lambda x: '"%s";' % x, use_cases))),
                     '{rank=max;%s}' % "".join(list(map(lambda x: '"%s";' % x, actors_second_half)))]
            counter = 0
            # for each cluster handle contents
            for key in s.C:
                counter = self.handle_cluster(s.C, key, counter, graph, s)
            for v in V: graph.append( u'"{}" {};'.format( quote( str( v ) ).encode('utf-8'), s.node_format( v, hide = v not in s.V ) ) )
            for e in E:
                graph.append( '"{}" -> "{}" {};'.format( quote( str( e[ 0 ] ) ), quote( str( e[ 1 ] ) ), s.edge_format( e, hide = e not in s.E ) ) )
            graph.append( '}' )
            graphs.append( '\n'.join( graph ) )
        return graphs

    def handle_cluster(self, C, key, counter, graph, s):
        graph.append('subgraph cluster_%i {' % counter)
        for node in C[key]:
            if isinstance(node, dict):
                for subkey in node:
                    counter = self.handle_cluster(node, subkey, counter, graph, s)
            else:
                graph.append('"{}" {};'.format(quote(str(node)), s.node_format(node)))
        if key in s.cV and not key in s.hC:
            graph.append('color=%s' % CLUSTER_COLOR)
        elif key in s.hC:
            graph.append('color=%s' % CLUSTER_HIGHLIGHT_COLOR)
        else:
            graph.append('color=%s' % CLUSTER_DEF_COLOR)
        graph.append('}')
        counter += 1
        return counter
