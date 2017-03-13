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

import project_database as db
import model_parser as parser
import diff_analyzer as anal
import graph_animator as anim
import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection


def _collect_stats(project_id):
    """
    Synopsis:
        Collects all the data neccessary to render stats pngs for a given project.
    :param project_id: ID of the project for which the stats are to be collected
    :returns stats: dictionary of stats
    """
    stats = {
        'nodes_over_time': list(),
        'edges_over_time': list(),
        'most_connected_obj': None,
        'least_connected_obj': None,
        'model_complexity_over_time': list(),
        'class_data_complexity': list(),
        'class_function_complexity': list()
    }

    mdjs = db.get_project_models(project_id = project_id)
    if not mdjs:
        return stats

    parsed, timeslice_array = _collect_quantity_stats(mdjs, stats)
    _collect_connectivity_stats(parsed, stats)
    _collect_complexity_stats(stats, timeslice_array)

    os.remove('degree_script.gvpr')
    os.remove('temp.dot')

    return stats


def _collect_complexity_stats(stats, timeslice_array):
    """
    Synopsis:
        Collects data about model complexity.
    :param stats: dictionary of stats where the results will be added
    :param timeslice_array: list of timeslices
    """
    for n, timeslice in enumerate(timeslice_array):
        min_amount_of_methods = 1e31 - 1
        total_amount_of_methods = 0
        min_amount_of_attributes = 1e31 - 1
        total_amount_of_attributes = 0
        attribute_nodes = 0
        method_nodes = 0

        for obj in timeslice:
            try:
                if len(obj.attributes) > 0:
                    min_amount_of_attributes = min(len(obj.attributes), min_amount_of_attributes)
                    total_amount_of_attributes += len(obj.attributes)
                    attribute_nodes += 1
                if len(obj.methods) > 0:
                    min_amount_of_methods = min(len(obj.methods), min_amount_of_methods)
                    total_amount_of_methods += len(obj.methods)
                    method_nodes += 1
            except AttributeError:
                continue

        stats['class_data_complexity'].append((1 - (float(attribute_nodes * min_amount_of_attributes) /
                                                    max(total_amount_of_attributes, 1))) ** 2 % 1)
        stats['class_function_complexity'].append((1 - (float(method_nodes * min_amount_of_methods) /
                                                        max(total_amount_of_methods, 1))) ** 2 % 1)


def _collect_connectivity_stats(parsed, stats):
    """
    Synopsis:
        Collects data about model connectivity.
    :param stats: dictionary of stats where the results will be added
    :param parsed: list of object trees
    """
    with open('degree_script.gvpr', 'w') as script:
        script.write('''
        N {
            printf("%s,%d,%d\n", $.name, $.indegree, $.outdegree);
        }
        ''')
    cmd = ['gvpr', '-f', 'degree_script.gvpr', 'temp.dot']
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    gvpr_result = list(map(lambda x: tuple([x.split(',')[0],
                                            int(x.split(',')[1]) + int(x.split(',')[2].replace('\r', ''))]),
                           p.stdout.read().split('\n')[:-1]))
    sorted_gvpr_result = sorted(gvpr_result, key = lambda x: x[1])
    most_connected_id = sorted_gvpr_result[-1]
    least_connected_id = sorted_gvpr_result[0]
    name_view = anal.find_tree_elem_by_id(parsed[-1],
                                          most_connected_id[0]).get_subview(view_type = 'UMLNameCompartmentView')
    name_subview = name_view.get_subview(view_type = 'LabelView',
                                         view_id = name_view.name_label)
    stats['most_connected_obj'] = name_subview.text
    name_view = anal.find_tree_elem_by_id(parsed[-1],
                                          least_connected_id[0]).get_subview(view_type = 'UMLNameCompartmentView')
    name_subview = name_view.get_subview(view_type = 'LabelView',
                                         view_id = name_view.name_label)
    stats['least_connected_obj'] = name_subview.text


def _collect_quantity_stats(mdjs, stats):
    """
    Synopsis:
        Collects data about model component quantity.
    :param mdjs: list of mdj file paths
    :param stats: dictionary of stats where the results will be added
    :returns parsed: list of object trees
    :returns timeslice_array: list of timeslices
    """
    parsed = list()
    timeslice_array = list()
    for n in range(1, len(mdjs) + 1):
        if n != 1:  # keep the last .dot file
            os.remove('temp.dot')

        parsed = parser.parse_models(mdj_array = mdjs[:n])
        timeslice_array, error_flag = anal.get_timeslices(parsed = parsed, diagram_id = 'all')
        graphs = anim.render_timeslices(timeslice_array = timeslice_array, disable_rendering = True)

        with open('temp.dot', 'w') as temp_dot_file:
            for line in graphs[-1].split('\n'):
                if 'style=invis' not in line:
                    temp_dot_file.write(line + '\n')

        cmd = ['gc', '-n', 'temp.dot']
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        nodes = int('0' + p.stdout.read().replace(' ', '').split('G')[0])
        stats['nodes_over_time'].append(nodes)

        cmd = ['gc', '-e', 'temp.dot']
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        edges = int('0' + p.stdout.read().replace(' ', '').split('G')[0])
        stats['edges_over_time'].append(edges)

        stats['model_complexity_over_time'].append(
            min((float(edges) / nodes) / (nodes * (nodes - 1) / 2) if nodes > 1 else 0, 1))
    return parsed, timeslice_array


def _radar_factory(dimensions):
    def draw_polygon():
        vertices = _unit_poly_verts(angles)
        return plt.Polygon(vertices, closed=True, edgecolor='black')

    class RadarAxes(PolarAxes):
        name = 'radar'

        def fill(self, *args, **kwargs):
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        @staticmethod
        def _close_line(line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(angles), labels, color='white', weight='bold', size='medium')

        def _gen_axes_patch(self):
            return draw_polygon()

        def _gen_axes_spines(self):
            verts = _unit_poly_verts(angles)
            verts.append(verts[0])

            spine = Spine(self, 'circle', Path(verts))
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    angles = np.linspace(0, np.pi * 2, dimensions, endpoint=False)
    angles += np.pi / 2

    register_projection(RadarAxes)
    return angles


def _unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r * np.cos(t) + x0, r * np.sin(t) + y0) for t in theta]
    return verts


def generate_statistics(project_id):
    """
    Synopsis:
        Generates statistics folder for a project.
    :param project_id: ID of the project for which statistics should be generated
    """
    stats = _collect_stats(project_id)
    with plt.rc_context({'axes.edgecolor': '#7d3c8c',
                         'xtick.color': 'white',
                         'ytick.color': 'white'}):
        fig = plt.figure(figsize=(10, 10), facecolor='#411f48')
        _generate_complexity_stats(fig, stats)
        _generate_quantity_stats(fig, stats)
        db.add_statistics(project_id, ['complexity.png', 'quantity.png'])


def _generate_quantity_stats(fig, stats):
    """
    Synopsis:
        Generates a quantity statistic png in the root folder from the given stats.
    :param fig: current matplotlib figure
    :param stats: stats file containing data from which to generate statistics
    """
    ax = fig.add_subplot(211)
    plt.xlim(0, len(stats['nodes_over_time']))
    plt.xticks(np.arange(1, len(stats['nodes_over_time']), 1.0))
    ax.set_title('Number of objects over time', weight = 'bold', size = 'medium', position = (0.5, 1.1),
                 horizontalalignment = 'center', verticalalignment = 'center', color = 'white')
    if len(stats['nodes_over_time']) > 1:
        ax.plot(range(len(stats['nodes_over_time'])), stats['nodes_over_time'], color = 'orange', linewidth = 4)
    else:
        plt.text(0.5, 0.5, 'Not enough data', horizontalalignment = 'center',
                 verticalalignment = 'center', transform = ax.transAxes, bbox = dict(facecolor = 'red', alpha = 0.5))
    ax = fig.add_subplot(212)
    plt.xlim(0, len(stats['edges_over_time']))
    plt.xticks(np.arange(1, len(stats['nodes_over_time']), 1.0))
    ax.set_title('Number of relations over time', weight = 'bold', size = 'medium', position = (0.5, 1.1),
                 horizontalalignment = 'center', verticalalignment = 'center', color = 'white')
    if len(stats['edges_over_time']) > 1:
        ax.plot(range(len(stats['edges_over_time'])), stats['edges_over_time'], color = 'orange', linewidth = 4)
    else:
        plt.text(0.5, 0.5, 'Not enough data', horizontalalignment = 'center',
                 verticalalignment = 'center', transform = ax.transAxes, bbox = dict(facecolor = 'red', alpha = 0.5))
    plt.tight_layout()
    plt.savefig('quantity.png', dpi = 90, facecolor = '#411f48')


def _generate_complexity_stats(fig, stats):
    """
    Synopsis:
        Generates a complexity statistic png in the root folder from the given stats.
    :param fig: current matplotlib figure
    :param stats: stats file containing data from which to generate statistics
    """
    if stats['nodes_over_time']:
        theta = _radar_factory(dimensions = 3)
        colors = ['orange', 'white', 'white']
        title = ['Model complexity', '\nData complexity', '\nMethod complexity']
        case_data = [[stats['model_complexity_over_time'][-1], stats['class_data_complexity'][-1],
                      stats['class_function_complexity'][-1]], [0, 0, 0], [1, 1, 1]]
        ax = fig.add_subplot(111, projection = 'radar')
        plt.rgrids([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], [''] * 9)
        for d, color in zip(case_data, colors):
            ax.plot(theta, d, color = color)
            ax.fill(theta, d, facecolor = color, alpha = 0.25)
        ax.set_varlabels(title)
    else:
        plt.text(0.5, 0.5, 'Not enough data', horizontalalignment = 'center',
                 verticalalignment = 'center', bbox = dict(facecolor = 'red', alpha = 0.5))
    plt.savefig('complexity.png', dpi = 90, facecolor = '#411f48')
    plt.clf()
