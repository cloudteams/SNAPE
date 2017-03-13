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

from libs.gvanim import Animation, render, gif


def render_timeslices(timeslice_array, disable_rendering=False):
    """
    Synopsis:
        Renders all timeslices to .png images. Returns graphviz .dot definitions for the images.
    :param timeslice_array: list of timeslices to be rendered
    :param disable_rendering: if True, only .dot files are returned and no images are rendered
    :returns graphs: .dot definitions of rendered images
    """
    ga = Animation()
    first = True

    use_cases = list()
    actors = list()
    uc_diagram = False

    for timeslice in timeslice_array:
        if first:
            first = False
        else:
            ga.next_step()

        for drawable in timeslice:
            obj_id, obj_type = drawable.draw(ga = ga)
            if obj_type == 'UMLUseCase':
                use_cases.append(obj_id)
                uc_diagram = True
            elif obj_type == 'UMLActor':
                actors.append(obj_id)
                uc_diagram = True

    graphs = ga.graphs(use_cases, actors, uc_diagram)
    if not disable_rendering:
        files = render(graphs, 'dfv', 'png', xdim = 9, ydim = 9)
        gif(files, 'dfv', delay = 140, xdim = 9, ydim = 9)
    return graphs
