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

def generate_log(timeslice_array, from_version = None, to_version = None):
    """
    Synopsis:
        Takes a list of timeslices and generates a textual changelog of the diff between revisions.
    :param timeslice_array: list of lists of Drawables
    :param from_version: optional starting index for changelog generation
    :param to_version: optional stopping index for changelog generation
    :returns log: string
    """
    if from_version is None:
        from_version = 1
    if to_version is None:
        to_version = len(timeslice_array)
    log = 80 * '-' + '\n'
    created_objects = list()
    timeless_objects = dict()
    for timeslice in timeslice_array[(from_version - 1):to_version]:
        objects = {
            'package': list(),
            'class': list(),
            'association': list(),
            'interface': list()
        }
        for drawable in timeslice:
            text, obj_id, obj_type, name = drawable.log(drawable.obj_id in created_objects)
            if text == 'No changes.':
                continue
            objects[obj_type].append((text, obj_id))
            timeless_objects[obj_id] = (obj_type, name)
            created_objects.append(obj_id)
        for key in objects:
            for obj in objects[key]:
                log = obj[0] + '\n' + log
        for drawable in created_objects:
            timeslice_ids = [obj.obj_id for obj in timeslice]
            if drawable not in timeslice_ids:
                entry = timeless_objects[drawable]
                log = 'The %s [%s] has been removed.' % entry + '\n' + log
                created_objects.remove(drawable)
        log = 80 * '-' + '\n' + log

    log = 'NEWEST CHANGES\n' + log + 'OLDEST CHANGES\n'
    return log
