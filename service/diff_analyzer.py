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

from drawables import *
import itertools
import traceback


def find_tree_elem_by_id(obj_tree, obj_id):
    """
    Synopsis:
        Searches the given object tree for an object with the given ID, and returns it.
        If no object is found, None is returned instead.
    :param obj_tree: root of the object tree to be searched
    :param obj_id: ID of the object to be searched for
    :returns obj: found object or None
    """
    if obj_tree.obj_id == obj_id:
        return obj_tree
    else:
        for elem in itertools.chain(obj_tree.owned_elements, obj_tree.owned_views, obj_tree.subviews):
            result = find_tree_elem_by_id(elem, obj_id)
            if result is not None:
                return result
    return None


def get_diagram_names_and_ids(parsed):
    """
    Synopsis:
        Given a list of parsed model files, returns a list of names and IDs of diagrams contained in them.
    :param parsed: list of parsed .mdj-files
    :returns diagram_list: list of (diagram name, diagram ID) tuples
    """
    def traverse_tree(node, root, diagrams):
        if 'Diagram' in node.type:
            diagrams.append((node.name, node.obj_id.replace('/', '')))

        for elem in itertools.chain(node.owned_elements, node.owned_views, node.subviews):
            diagrams = traverse_tree(elem, root, diagrams)

        return diagrams

    diagram_list = list()
    for p in parsed:
        diagram_list += traverse_tree(p, p, diagram_list)

    return diagram_list


def get_timeslices(parsed, diagram_id):
    """
    Synopsis:
        Takes a list of parsed .mdj files and turns them into a list of timeslices.
        (i.e. a list of lists of Drawable objects as specified in drawable.py)
    :param parsed: list or parsed .mdj-files
    :param diagram_id: ID of the diagram to be rendered
    :returns timeslice_array: list of timeslices
    :returns error_flag: indicator that an error occurrec during execution
    """
    global timeslice_array
    timeslice_array = list()
    error_flag = False

    try:
        def contains_class(prev_timeslice, obj_id):
            for objct in prev_timeslice:
                if objct.obj_id == obj_id:
                    return objct
            return None

        def traverse_tree(node, root, diagram_id, timeslice):
            """
            Synopsis:
                Recursively traverses a parsed tree and transforms nodes into Drawable objects.
            :param node: current node during traversal
            :param root: parse tree top level node
            :param diagram_id: ID of the diagram to be rendered
            :param timeslice: current timeslice to which the Drawables are added
            :returns timeslice: current timeslice
            """
            global timeslice_array

            skip_node = False
            diagram = node

            if diagram_id != 'all' and node.obj_id.replace('/', '') != diagram_id:
                skip_node = True

            for view in diagram.owned_views:
                if skip_node:
                    break
                if view.type == 'UMLClassView':

                    class_model = find_tree_elem_by_id(root, view.model)

                    attributes = []
                    attribute_view = view.get_subview(view_type = 'UMLAttributeCompartmentView')
                    for attr in attribute_view.subviews:
                        if attr.type == 'UMLAttributeView':
                            attributes.append(attr.text)

                    methods = []
                    method_view = view.get_subview(view_type = 'UMLOperationCompartmentView')
                    for op in method_view.subviews:
                        if op.type == 'UMLOperationView':
                            methods.append(op.text)

                    new_class = UMLClass(obj_id = view.obj_id,
                                         name = class_model.name,
                                         methods = methods,
                                         attributes = attributes,
                                         stereotype = class_model.stereotype)

                    changes = []

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_class.obj_id)

                        if obj:
                            if obj.name != new_class.name:
                                changes.append('Name')
                            if obj.methods != new_class.methods:
                                changes.append('Methods')
                            if obj.attributes != new_class.attributes:
                                changes.append('Attributes')
                        else:
                            changes.append('Created')

                    new_class.has_changed(changes)

                    timeslice.append(new_class)

                elif view.type == 'UMLInterfaceView':

                    name_view = view.get_subview(view_type = 'UMLNameCompartmentView')
                    name_subview = name_view.get_subview(view_type = 'LabelView',
                                                         view_id = name_view.name_label)

                    new_interface = UMLInterface(obj_id = view.obj_id,
                                                 name = name_subview.text)

                    changes = []

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_interface.obj_id)

                        if obj:
                            if obj.name != new_interface.name:
                                changes.append('Name')
                        else:
                            changes.append('Created')

                    new_interface.has_changed(changes)

                    timeslice.append(new_interface)

                elif view.type in ['UMLAssociationView', 'UMLDependencyView', 'UMLGeneralizationView',
                                   'UMLInterfaceRealizationView']:

                    association = find_tree_elem_by_id(root, view.model)

                    new_association = UMLAssociation(obj_id = view.obj_id,
                                                     from_id = view.tail,
                                                     to_id = view.head,
                                                     name = association.name,
                                                     directed = not association.navigable_end1,
                                                     aggregation = association.aggregation2,
                                                     multiplicities = (association.multiplicity1,
                                                                       association.multiplicity2),
                                                     dependency = view.type == 'UMLDependencyView',
                                                     generalization = view.type == 'UMLGeneralizationView',
                                                     realization = view.type == 'UMLInterfaceRealizationView')

                    changes = []

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_association.obj_id)

                        if obj:
                            if obj.name != new_association.name:
                                changes.append('Name')
                            if obj.from_id != new_association.from_id:
                                changes.append('Tail')
                            if obj.to_id != new_association.to_id:
                                changes.append('Head')
                            if obj.directed != new_association.directed:
                                changes.append('Directedness')
                            if obj.aggregation != new_association.aggregation:
                                changes.append('Aggregatedness')
                        else:
                            changes.append('Created')

                    if changes:
                        new_association.has_changed(changes)

                    timeslice.append(new_association)

                elif view.type == 'UMLPackageView':
                    new_package = UMLPackage(obj_id = view.obj_id,
                                             name = find_tree_elem_by_id(view, view.name_compartment).text,
                                             parent_id = None,
                                             nodes = view.contained_views,
                                             subclusters = []
                                             )

                    changes = []

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_package.obj_id)

                        if obj:
                            if obj.name != new_package.name:
                                changes.append('Name')
                            if obj.parent_id != new_package.parent_id:
                                changes.append('Parent package')
                            if obj.nodes != new_package.nodes:
                                changes.append('Contained elements')
                            if obj.subclusters != new_package.subclusters:
                                changes.append('Subclusters changed')
                        else:
                            changes.append('Created')

                    if changes:
                        new_package.has_changed(changes)

                    timeslice.append(new_package)

                elif view.type == 'UMLUseCaseView':

                    new_usecase = UMLUseCase(obj_id = view.obj_id,
                                             name = find_tree_elem_by_id
                                             (root, find_tree_elem_by_id(view, view.name_compartment).model).name
                                             )

                    changes = list()

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_usecase.obj_id)

                        if obj:
                            if obj.name != new_usecase.name:
                                changes.append('Name')
                        else:
                            changes.append('Created')

                    if changes:
                        new_usecase.has_changed(changes)

                    timeslice.append(new_usecase)

                elif view.type == 'UMLActorView':

                    new_actor = UMLActor(obj_id = view.obj_id,
                                         name = find_tree_elem_by_id(root, view.model).name
                                         )

                    changes = list()

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_actor.obj_id)

                        if obj:
                            if obj.name != new_actor.name:
                                changes.append('Name')
                        else:
                            changes.append('Created')

                    if changes:
                        new_actor.has_changed(changes)

                    timeslice.append(new_actor)

                elif view.type in ['UMLIncludeView', 'UMLExtendView']:

                    if view.type == 'UMLIncludeView':
                        uml_class = UMLInclusion
                    else:
                        uml_class = UMLExtension

                    new_inex = uml_class(obj_id = view.obj_id,
                                         name = find_tree_elem_by_id(root, view.model).name,
                                         from_id = view.tail,
                                         to_id = view.head
                                         )

                    changes = list()

                    if timeslice_array:
                        obj = contains_class(timeslice_array[-1], new_inex.obj_id)

                        if obj:
                            if obj.name != new_inex.name:
                                changes.append('Name')
                            if obj.from_id != new_inex.from_id:
                                changes.append('Tail')
                            if obj.to_id != new_inex.to_id:
                                changes.append('Head')
                        else:
                            changes.append('Created')

                    if changes:
                        new_inex.has_changed(changes)

                    timeslice.append(new_inex)

            for elem in itertools.chain(node.owned_elements, node.owned_views, node.subviews):
                timeslice = traverse_tree(elem, root, diagram_id, timeslice)

            return timeslice

        for p in parsed:
            timeslice_array.append(traverse_tree(node = p, root = p, diagram_id = diagram_id, timeslice = list()))

    except AttributeError:
        traceback.print_exc()
        timeslice_array = []
        error_flag = True
    except TypeError:
        traceback.print_exc()
        timeslice_array = []
        error_flag = True
    except ValueError:
        traceback.print_exc()
        timeslice_array = []
        error_flag = True
    except NameError:
        traceback.print_exc()
        timeslice_array = []
        error_flag = True
    except KeyError:
        traceback.print_exc()
        timeslice_array = []
        error_flag = True
    finally:
        return timeslice_array, error_flag
