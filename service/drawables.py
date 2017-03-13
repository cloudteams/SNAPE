# coding=utf-8

"""
Copyright (c) 2016, 2017 FZI Forschungszentrum Informatik am Karlsruher Institut für Technologie

This file is part of SNAPE.

SNAPE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SNAPE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SNAPE.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
This file contains all supported UML Objects that can be rendered.
A Drawable at least implements the following:
1. draw(ga) - a function that draws it into the given graph animator
2. log(created) - a function that documents the Drawables status textually
3. __eq__(other) - comparison magic function
"""

import libs.gvanim.config


class Drawable(object):
    def __init__(self, obj_id):
        self.obj_id = obj_id
        self.changes = []

    def draw(self, ga):
        print 'The Drawable with the ID %s has no implemented draw function yet.' % str(self.obj_id)

    def log(self, created):
        return 'Unknown change.', self.obj_id, 'unknown', 'unknown'

    def __eq__(self, obj):
        print 'The Drawable with the ID %s has no implemented is_equal_to function yet.' % str(self.obj_id)

    def has_changed(self, changes):
        self.changes = changes

    @staticmethod
    def _uml_label(name, methods = None, attributes = None, stereotype = None):
        string = ''
        if stereotype:
            string += '<{&#171;<i>%s</i>&#187;<br/>%s|' % (name, stereotype)
        else:
            string += '<{%s|' % name
        if attributes is not None:
            for a in attributes:
                string += a + '<br/>'
        string += '|'
        if methods is not None:
            for m in methods:
                string += m + '<br/>'
        string += '}>'
        return string

    @staticmethod
    def _new_node(nid, ga, options = None, highlight = False):
        ga.add_node(nid, options = options)
        if highlight:
            ga.highlight_node(nid)

    @staticmethod
    def _new_edge(from_id, to_id, ga, options = None, highlight = False):
        ga.add_edge(to_id, from_id, options = options)
        if highlight:
            ga.highlight_edge(to_id, from_id)

    @staticmethod
    def _new_class(cid, name, ga, methods = None, attributes = None):
        Drawable._new_node(cid, ga = ga, options = None)
        ga.label_node(cid, Drawable._uml_label(name = name, methods = methods, attributes = attributes))

    @staticmethod
    def _new_association(from_id, to_id, ga, name = '', multiplicities = (None, None),
                         directed = False, highlight = False, stereotype = None):
        if stereotype:
            label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (name, stereotype)
        else:
            label = 'label=" %s "' % name

        options = [label, 'fontcolor="%s"' % libs.gvanim.config.EDGE_FONT_COLOR]

        if not directed:
            options.append('arrowtail=none')

        if multiplicities[0] is not None:
            options.append('headlabel="  %s  "' % multiplicities[0])
        if multiplicities[1] is not None:
            options.append('taillabel="  %s  "' % multiplicities[1])

        if len(options) == 0:
            options = None
        else:
            options = '[' + ','.join(options) + ']'

        Drawable._new_edge(from_id = from_id, to_id = to_id, options = options, ga = ga, highlight = highlight)

    @staticmethod
    def _new_aggregation(from_id, to_id, ga, name = '', multiplicities = (None, None),
                         highlight = False, stereotype = None):
        if stereotype:
            label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (name, stereotype)
        else:
            label = 'label=" %s "' % name
        options = [
            label,
            'arrowtail=ediamond'
        ]

        Drawable._build_new_connection(from_id, ga, highlight, multiplicities, options, to_id)

    @staticmethod
    def _new_composition(from_id, to_id, ga, name = '', multiplicities = (None, None),
                         highlight = False, stereotype = None):
        if stereotype:
            label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (name, stereotype)
        else:
            label = 'label=" %s "' % name
        options = [
            label,
            'arrowtail=diamond'
        ]

        Drawable._build_new_connection(from_id, ga, highlight, multiplicities, options, to_id)

    @staticmethod
    def _new_generalization(from_id, to_id, ga, name = '', multiplicities = (None, None),
                            highlight = False, stereotype = None):
        if stereotype:
            label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (name, stereotype)
        else:
            label = 'label=" %s "' % name
        options = [
            label,
            'arrowtail=empty'
        ]

        Drawable._build_new_connection(from_id, ga, highlight, multiplicities, options, to_id)

    @staticmethod
    def _new_realization(from_id, to_id, ga, name = '', multiplicities = (None, None),
                         highlight = False, stereotype = None):
        if stereotype:
            label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (name, stereotype)
        else:
            label = 'label=" %s "' % name
        options = [
            label,
            'arrowtail=empty',
            'style=dashed'
        ]

        Drawable._build_new_connection(from_id, ga, highlight, multiplicities, options, to_id)

    @staticmethod
    def _new_dependency(from_id, to_id, ga, name = '', multiplicities = (None, None),
                        highlight = False, stereotype = None):
        if stereotype:
            label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (name, stereotype)
        else:
            label = 'label=" %s "' % name
        options = [
            label,
            'style=dashed'
        ]

        Drawable._build_new_connection(from_id, ga, highlight, multiplicities, options, to_id)

    @staticmethod
    def _build_new_connection(from_id, ga, highlight, multiplicities, options, to_id):
        options.append('fontcolor="%s"' % libs.gvanim.config.EDGE_FONT_COLOR)
        if multiplicities[0] is not None:
            options.append('headlabel="  %s  "' % multiplicities[0])
        if multiplicities[1] is not None:
            options.append('taillabel="  %s  "' % multiplicities[1])
        if len(options) == 0:
            options = None
        else:
            options = '[' + ','.join(options) + ']'
        Drawable._new_edge(from_id = from_id, to_id = to_id, options = options, ga = ga, highlight = highlight)

    @staticmethod
    def _remove_class(cid, ga):
        ga.remove_node(cid, ga)

    @staticmethod
    def _remove_connection(from_id, to_id, ga):
        ga.remove_edge(to_id, from_id, ga)

    @staticmethod
    def _update_class(cid, name, ga, methods = None, attributes = None):
        ga.label_node(cid, Drawable._uml_label(name = name, methods = methods, attributes = attributes))
        ga.highlight_node(cid)

    @staticmethod
    def _update_association(from_id, to_id, ga, name = '', multiplicities = (None, None), directed = False):
        Drawable._remove_connection(from_id = from_id, to_id = to_id, ga = ga)
        Drawable._new_association(from_id = from_id, to_id = to_id, name = name,
                                  multiplicities = multiplicities, directed = directed, ga = ga)

    @staticmethod
    def _update_generalization(from_id, to_id, ga, name = '', multiplicities = (None, None)):
        Drawable._remove_connection(from_id = from_id, to_id = to_id, ga = ga)
        Drawable._new_generalization(from_id = from_id, to_id = to_id, name = name, multiplicities = multiplicities,
                                     ga = ga)

    @staticmethod
    def _update_composition(from_id, to_id, ga, name = '', multiplicities = (None, None)):
        Drawable._remove_connection(from_id = from_id, to_id = to_id, ga = ga)
        Drawable._new_composition(from_id = from_id, to_id = to_id, name = name, multiplicities = multiplicities,
                                  ga = ga)

    @staticmethod
    def _update_aggregation(from_id, to_id, ga, name = '', multiplicities = (None, None)):
        Drawable._remove_connection(from_id = from_id, to_id = to_id, ga = ga)
        Drawable._new_aggregation(from_id = from_id, to_id = to_id, name = name, multiplicities = multiplicities,
                                  ga = ga)

    @staticmethod
    def _update_dependency(from_id, to_id, ga, name = '', multiplicities = (None, None)):
        Drawable._remove_connection(from_id = from_id, to_id = to_id, ga = ga)
        Drawable._new_dependency(from_id = from_id, to_id = to_id, name = name, multiplicities = multiplicities,
                                 ga = ga)

    @staticmethod
    def _update_realization(from_id, to_id, ga, name = '', multiplicities = (None, None)):
        Drawable._remove_connection(from_id = from_id, to_id = to_id, ga = ga)
        Drawable._new_realization(from_id = from_id, to_id = to_id, name = name, multiplicities = multiplicities,
                                  ga = ga)


class UMLClass(Drawable):
    def __init__(self, obj_id, name = '', methods = None, attributes = None, stereotype = None):
        Drawable.__init__(self, obj_id)
        self.name = name
        self.methods = methods
        self.attributes = attributes
        self.stereotype = stereotype

    def draw(self, ga):
        Drawable._new_node(self.obj_id, options = 'fontcolor="%s",shape=record' % libs.gvanim.config.NODE_FONT_COLOR,
                           ga = ga, highlight = bool(self.changes))
        ga.label_node(self.obj_id, Drawable._uml_label(name = self.name, methods = self.methods,
                                                       attributes = self.attributes, stereotype = self.stereotype))

        return self.obj_id, 'UMLClass'

    def log(self, created):
        if not created:
            return 'The class [%s] was added.' % self.name, self.obj_id, 'class', self.name
        else:
            if self.changes:
                return 'The class [{0}] was changed. {1}'.format(self.name, self.changes).replace('\'', ''), \
                       self.obj_id, 'class', self.name
            else:
                return 'No changes.', self.obj_id, 'class', self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        if not hasattr(obj, 'methods') or obj.methods != self.methods:
            return False
        if not hasattr(obj, 'attributes') or obj.attributes != self.attributes:
            return False
        return True


class UMLInterface(Drawable):
    def __init__(self, obj_id, name = ''):
        Drawable.__init__(self, obj_id)
        self.name = name

    def draw(self, ga):
        Drawable._new_node(self.obj_id, options = 'shape=circle, fontcolor="%s"' % libs.gvanim.config.NODE_FONT_COLOR,
                           ga = ga, highlight = bool(self.changes))
        ga.label_node(self.obj_id, '"' + self.name + '"')

        return self.obj_id, 'UMLInterface'

    def log(self, created):
        if not created:
            return 'The interface [%s] was added.' % self.name, self.obj_id, 'interface', self.name
        else:
            if self.changes:
                return 'The interface [{0}] was changed. {1}'.format(self.name, self.changes).replace('\'', ''), \
                       self.obj_id, 'interface', self.name
            else:
                return 'No changes.', self.obj_id, 'interface', self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        return True


class UMLAssociation(Drawable):
    def __init__(self, obj_id, from_id, to_id, name = '', multiplicities = (None, None),
                 directed = False, aggregation = False, dependency = False, generalization = False,
                 realization = False, stereotype = None):
        Drawable.__init__(self, obj_id)
        self.from_id = from_id
        self.to_id = to_id
        self.name = name
        if self.name is None:
            self.name = ''
        self.multiplicities = multiplicities
        self.directed = directed
        self.aggregation = aggregation
        self.dependency = dependency
        self.generalization = generalization
        self.realization = realization
        self.stereotype = stereotype

    def draw(self, ga):
        if self.aggregation == u'shared':
            Drawable._new_aggregation(from_id = self.from_id, to_id = self.to_id,
                                      ga = ga, name = self.name, multiplicities = self.multiplicities,
                                      highlight = bool(self.changes))
        elif self.aggregation == u'composite':
            Drawable._new_composition(from_id = self.from_id, to_id = self.to_id,
                                      ga = ga, name = self.name, multiplicities = self.multiplicities,
                                      highlight = bool(self.changes))
        elif self.dependency:
            Drawable._new_dependency(from_id = self.from_id, to_id = self.to_id,
                                     ga = ga, name = self.name, multiplicities = self.multiplicities,
                                     highlight = bool(self.changes))
        elif self.generalization:
            Drawable._new_generalization(from_id = self.from_id, to_id = self.to_id,
                                         ga = ga, name = self.name, multiplicities = self.multiplicities,
                                         highlight = bool(self.changes))
        elif self.realization:
            Drawable._new_realization(from_id = self.from_id, to_id = self.to_id,
                                      ga = ga, name = self.name, multiplicities = self.multiplicities,
                                      highlight = bool(self.changes))
        else:
            options = ['label=" %s "' % self.name, 'fontcolor="%s"' % libs.gvanim.config.EDGE_FONT_COLOR]
            if not self.directed:
                options.append('arrowtail=none')
            if self.multiplicities[0] is not None:
                options.append('headlabel="  %s  "' % self.multiplicities[0])
            if self.multiplicities[1] is not None:
                options.append('taillabel="  %s  "' % self.multiplicities[1])
            if len(options) == 0:
                options = None
            else:
                options = '[' + ','.join(options) + ']'

            Drawable._new_edge(from_id = self.from_id, to_id = self.to_id, options = options, ga = ga,
                               highlight = bool(self.changes))

        return self.obj_id, 'UMLAssociation'

    def log(self, created):
        if not created:
            return 'The association [%s] was added.' % self.name, self.obj_id, 'association', self.name
        else:
            if self.changes:
                return 'The association [{0}] was changed. ({1})'.format(self.name, self.changes), \
                       self.obj_id, 'association', self.name
            else:
                return 'No changes.', self.obj_id, 'association', self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'from_id') or obj.from_id != self.from_id:
            return False
        if not hasattr(obj, 'to_id') or obj.to_id != self.to_id:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        if not hasattr(obj, 'multiplicities') or obj.multiplicities != self.multiplicities:
            return False
        if not hasattr(obj, 'directed') or obj.directed != self.directed:
            return False
        return True


class UMLPackage(Drawable):
    def __init__(self, obj_id, parent_id = None, name = '', nodes = None, subclusters = None):
        Drawable.__init__(self, obj_id)
        self.name = name
        if self.name is None:
            self.name = ''
        self.nodes = nodes
        self.subclusters = subclusters
        self.parent_id = parent_id

        if self.nodes is None:
            self.nodes = list()
        if self.subclusters is None:
            self.subclusters = list()

    def draw(self, ga):
        ga.create_cluster(cluster_id = self.obj_id, parent_cluster_id = self.parent_id)
        ga.make_cluster_visible(cluster_id = self.obj_id, highlight = self.changes)
        for node_id in self.nodes:
            ga.add_node_to_cluster(cluster_id = self.obj_id, node_id = node_id)
        for subcluster in self.subclusters:
            ga.create_cluster(cluster_id = subcluster, parent_cluster_id = self.obj_id)
            ga.make_cluster_visible(cluster_id = subcluster, highlight = False)

        return self.obj_id, 'UMLPackage'

    def log(self, created):
        if not created:
            return 'The package [%s] was added.' % self.name, self.obj_id, 'package', self.name
        else:
            if self.changes:
                return 'The package [{0}] was changed. ({1})'.format(self.name, self.changes), \
                       self.obj_id, 'package', self.name
            else:
                return 'No changes.', self.obj_id, 'package', self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'nodes') or obj.nodes != self.nodes:
            return False
        if not hasattr(obj, 'subclusters') or obj.subclusters != self.subclusters:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        if not hasattr(obj, 'parent_id') or obj.parent_id != self.parent_id:
            return False
        return True


class UMLUseCase(Drawable):
    def __init__(self, obj_id, name = ''):
        Drawable.__init__(self, obj_id)
        self.name = name

    def draw(self, ga):
        Drawable._new_node(self.obj_id, options = 'fontcolor="%s",shape=ellipse,height=0.5,rank="sink"' %
                                                  libs.gvanim.config.NODE_FONT_COLOR,
                           ga = ga, highlight = bool(self.changes))
        ga.label_node(self.obj_id, '"' + self.name + '"')

        return self.obj_id, 'UMLUseCase'

    def log(self, created):
        if not created:
            return 'The use-case [%s] was added.' % self.name, self.obj_id, 'usecase', self.name
        else:
            if self.changes:
                return 'The use-case [{0}] was changed. ({1})'.format(self.name, self.changes), \
                       self.obj_id, 'usecase', self.name
            else:
                return 'No changes.', self.obj_id, 'usecase', self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        return True


class UMLActor(Drawable):
    def __init__(self, obj_id, name = ''):
        Drawable.__init__(self, obj_id)
        self.name = name

    def draw(self, ga):
        Drawable._new_node(self.obj_id,
                           options = 'fontcolor="%s",shape=none,image="resources/umlactor.png",fillcolor=transparent,'
                                     'width=0.5,height=0.5,rank="source"' %
                           libs.gvanim.config.NODE_FONT_COLOR, ga = ga,
                           highlight = bool(self.changes))
        ga.label_node(self.obj_id, '"' + ' \\n' * 9 + self.name + '"')

        return self.obj_id, 'UMLActor'

    def log(self, created):
        if not created:
            return 'The actor [%s] was added.' % self.name, self.obj_id, 'actor', self.name
        else:
            if self.changes:
                return 'The actor [{0}] was changed. ({1})'.format(self.name, self.changes), \
                       self.obj_id, 'actor', self.name
            else:
                return 'No changes.', self.obj_id, 'actor', self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        return True


class UMLExtensionInclude(Drawable):
    def __init__(self, obj_id, from_id, to_id, name = '', obj_type = 'inclusion'):
        Drawable.__init__(self, obj_id)
        self.from_id = from_id
        self.to_id = to_id
        self.name = name
        self.obj_type = obj_type
        if self.name is None:
            self.name = ''

    def draw(self, ga):
        label = 'label=<%s<br/>&#171;<i>%s</i>&#187;>' % (self.name, self.obj_type)
        options = [label, 'fontcolor="%s"' % libs.gvanim.config.EDGE_FONT_COLOR]
        if len(options) == 0:
            options = None
        else:
            options = '[' + ','.join(options) + ']'

        Drawable._new_edge(from_id = self.from_id, to_id = self.to_id, options = options, ga = ga,
                           highlight = bool(self.changes))

        return self.obj_id, 'UMLExtensionInclude'

    def log(self, created):
        if not created:
            return 'The %s [%s] was added.' % (self.obj_type, self.name), self.obj_id, self.obj_type, self.name
        else:
            if self.changes:
                return 'The {2} [{0}] was changed. ({1})'.format(self.name, self.changes, self.obj_type), \
                       self.obj_id, self.obj_type, self.name
            else:
                return 'No changes.', self.obj_id, self.obj_type, self.name

    def __eq__(self, obj):
        if not hasattr(obj, 'obj_id') or obj.obj_id != self.obj_id:
            return False
        if not hasattr(obj, 'from_id') or obj.from_id != self.from_id:
            return False
        if not hasattr(obj, 'to_id') or obj.to_id != self.to_id:
            return False
        if not hasattr(obj, 'name') or obj.name != self.name:
            return False
        return True


class UMLExtension(UMLExtensionInclude):
    def __init__(self, obj_id, from_id, to_id, name = ''):
        UMLExtensionInclude.__init__(self, obj_id = obj_id, from_id = from_id, to_id = to_id,
                                     name = name, obj_type = 'extension')


class UMLInclusion(UMLExtensionInclude):
    def __init__(self, obj_id, from_id, to_id, name = ''):
        UMLExtensionInclude.__init__(self, obj_id = obj_id, from_id = from_id, to_id = to_id,
                                     name = name, obj_type = 'inclusion')


class UMLInvisibleNode(Drawable):
    def __init__(self):
        Drawable.__init__(self, 'invisibleNode')

    def draw(self, ga):
        Drawable._new_node(self.obj_id, options = 'fontcolor=transparent,shape=none,label=""',
                           ga = ga, highlight = bool(self.changes))
        ga.label_node(self.obj_id, ' ')
        return self.obj_id, 'UMLInvisible'

    def log(self, created):
        return ''

    def __eq__(self, obj):
        return False
