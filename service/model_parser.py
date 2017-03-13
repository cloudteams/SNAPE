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

import json
import traceback


class Entry(object):
    """
    Synopsis:
        Entry objects are nodes of the parse tree of a .mdj file. They contain fields for all information relevant
        to render at least one type of Drawable. Fields are filled while traversing the .mdj file.
    """
    def __init__(self,
                 name = 'Unnamed',
                 obj_id = None,
                 node_type = None,
                 text = '',
                 level = 0,
                 name_label = None,
                 stereotype = None,
                 head = None, tail = None,
                 line_style = None,
                 navigable_end1 = False,
                 navigable_end2 = False,
                 model = None,
                 contained_views = None,
                 name_compartment = None,
                 aggregation1 = False,
                 aggregation2 = False,
                 multiplicity1 = '',
                 multiplicity2 = ''):
        self.level = level
        self.text = text
        self.name = name
        self.obj_id = obj_id
        self.type = node_type

        # UMLClass
        self.name_label = name_label
        self.stereotype = stereotype

        # UMLAssociation
        self.head = head
        self.tail = tail
        self.line_style = line_style
        self.navigable_end1 = navigable_end1
        self.navigable_end2 = navigable_end2
        self.model = model
        self.aggregation1 = aggregation1
        self.aggregation2 = aggregation2
        self.multiplicity1 = multiplicity1
        self.multiplicity2 = multiplicity2

        # UMLPackage
        self.contained_views = contained_views
        if self.contained_views is None:
            self.contained_views = []
        self.name_compartment = name_compartment

        self.owned_elements = []
        self.owned_views = []
        self.subviews = []

    def __repr__(self):
        owned_element_names = ''
        owned_view_names = ''
        sub_view_names = ''
        for elem in self.owned_elements:
            owned_element_names += str(elem.obj_id)
        for view in self.owned_views:
            owned_view_names += str(view.obj_id)
        for subview in self.subviews:
            sub_view_names += str(subview.obj_id)
        return "Type: %s, Level: %i, Owned Elements: %s, Owned Views: %s, Subviews: %s" \
               % (self.type, self.level, owned_element_names, owned_view_names, sub_view_names)

    def __eq__(self, other):
        if len(self.owned_elements) != len(other.owned_elements):
            return False
        for i in range(len(self.owned_elements)):
            if not self.owned_elements[i].__eq__(other.owned_elements[i]):
                return False

        if len(self.owned_views) != len(other.owned_views):
            return False
        for i in range(len(self.owned_views)):
            if not self.owned_views[i].__eq__(other.owned_views[i]):
                return False

        if len(self.subviews) != len(other.subviews):
            return False
        for i in range(len(self.subviews)):
            if not self.subviews[i].__eq__(other.subviews[i]):
                return False

        return self.level == other.level and \
            self.text == other.text and \
            self.name == other.name and \
            self.obj_id == other.obj_id and \
            self.type == other.type and \
            self.name_label == other.name_label and \
            self.stereotype == other.stereotype and \
            self.head == other.head and \
            self.tail == other.tail and \
            self.line_style == other.line_style and \
            self.navigable_end1 == other.navigable_end1 and \
            self.navigable_end2 == other.navigable_end2 and \
            self.model == other.model and \
            self.contained_views == other.contained_views and \
            self.contained_views == other.contained_views and \
            self.name_compartment == other.name_compartment and \
            self.owned_elements == other.owned_elements and \
            self.owned_views == other.owned_views and \
            self.subviews == other.subviews and \
            self.aggregation1 == other.aggregation1 and \
            self.aggregation2 == other.aggregation2 and \
            self.multiplicity1 == other.multiplicity1 and \
            self.multiplicity2 == other.multiplicity2

    def add_owned_element(self, elem):
        self.owned_elements.append(elem)

    def add_owned_view(self, view):
        self.owned_views.append(view)

    def add_subview(self, subview):
        self.subviews.append(subview)

    def get_owned_element(self, node_type):
        result = None
        for elem in self.owned_elements:
            if elem.type == node_type:
                result = elem

        return result

    def get_owned_view(self, view_type):
        result = None
        for view in self.owned_views:
            if view.type == view_type:
                result = view

        return result

    def get_subview(self, view_type, view_id = None):
        result = None
        for subview in self.subviews:
            if subview.type == view_type and (view_id is None or view_id == subview.obj_id):
                result = subview

        return result


def __load_json(filename):
    return json.loads(open(filename).read().decode('utf-8'))


def __tree_builder(obj, level = 0):
    contained_views = obj.get('containedViews', [])
    refined_contained_views = []
    for elem in contained_views:
        ref = elem.get('$ref', None)
        if ref is not None:
            refined_contained_views.append(ref)

    node = Entry(name = obj.get('name', None),
                 node_type = obj.get('_type', None),
                 obj_id = obj.get('_id', None),
                 text = obj.get('text', None),
                 level = level,
                 name_label = obj.get('nameLabel', {}).get('$ref', None),
                 stereotype = obj.get('stereotype', None),
                 head = obj.get('head', {}).get('$ref', None),
                 tail = obj.get('tail', {}).get('$ref', None),
                 line_style = obj.get('lineStyle', 0),
                 navigable_end1 = obj.get('end1', {}).get('navigable', False),
                 navigable_end2 = obj.get('end2', {}).get('navigable', False),
                 model = obj.get('model', {}).get('$ref', None),
                 contained_views = refined_contained_views,
                 name_compartment = obj.get('nameCompartment', {}).get('$ref', None),
                 aggregation1 = obj.get('end1', {}).get('aggregation', False),
                 aggregation2 = obj.get('end2', {}).get('aggregation', False),
                 multiplicity1 = obj.get('end1', {}).get('multiplicity', ''),
                 multiplicity2 = obj.get('end2', {}).get('multiplicity', ''))
    for elem in obj.get('ownedElements', []):
        node.add_owned_element(__tree_builder(elem, level = level + 1))
    for view in obj.get('ownedViews', []):
        node.add_owned_view(__tree_builder(view, level = level + 1))
    for subview in obj.get('subViews', []):
        node.add_subview(__tree_builder(subview, level = level + 1))
    return node


def __create_obj_tree(mdj_file):
    obj = __load_json(mdj_file)
    tree = __tree_builder(obj)
    return tree


def parse_models(mdj_array):
    """
    Synopsis:
        Takes a list of .mdj files and parses them into an object tree for the diff_analyzer.
    :param mdj_array: list of paths to .mdj files to be parsed
    :returns parsed_models: list of object trees
    """
    parsed_models = list()
    try:
        for mdj in mdj_array:
            parsed_models.append(__create_obj_tree(mdj))
    except AttributeError:
        traceback.print_exc()
        parsed_models = []
    except TypeError:
        traceback.print_exc()
        parsed_models = []
    except ValueError:
        traceback.print_exc()
        parsed_models = []
    except NameError:
        traceback.print_exc()
        parsed_models = []
    except KeyError:
        traceback.print_exc()
        parsed_models = []
    finally:
        return parsed_models
