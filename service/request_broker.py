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

from flask import Flask, request, abort, jsonify, send_file
from flask_cors import CORS
import project_database as db
import model_parser as parser
import diff_analyzer as anal
import graph_animator as anim
import textlog_generator as gen
import datetime
import time
from shutil import copyfile
from security import *
import portalocker as plocker
from statistic_collector import generate_statistics
import socket


app = Flask(__name__)
app.config['APPLICATION_ROOT'] = ROOT
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/snape/1.0/projects', methods=['POST'])
def create_project():
    """
    Synopsis:
        Creates a new project inside the system. This includes
        1. a database directory
        2. a set of valid user tokens
        3. a unique project ID
        This function claims the *shelve.lock* and the *db.lock* system locks.
    Status Codes:
        201: successful
        400: password or token count not found in request
        403: password invalid
        413: too many tokens requested
    :returns response: JSON-object containing
        1. unique new project ID
        2. set of valid user tokens
        3. return message
    """
    if not request.json or 'password' not in request.json or 'token_count' not in request.json \
            or not is_int_castable(request.json['token_count']):
        abort(400)  # Bad request

    if not server_password_is_valid(request.json['password']):
        abort(403)  # Forbidden

    if int(request.json['token_count']) > TOKEN_MAX_REQUEST:
        abort(413)  # Payload too large

    with open(os.path.join('shelve.lock'), 'a', 0) as shelve_lock:
        plocker.lock(shelve_lock, plocker.LOCK_EX)
        c = shelve.open('id_counter')
        try:
            new_project_id = c['counter']
            c['counter'] = new_project_id + 1
        finally:
            c.close()

        token_file = shelve.open('token_list')
        new_tokens = []
        try:
            token_list = token_file['token_list']
            while len(new_tokens) < int(request.json['token_count']):
                new_token = generate_token(token_list)
                new_tokens.append(new_token)
                token_list.append(new_token)
            token_file['token_list'] = token_list
            token_file[str(new_project_id)] = new_tokens
        finally:
            token_file.close()

    db.create_project(project_id = new_project_id)

    return jsonify({'new_project_id': new_project_id,
                    'generated_tokens': new_tokens,
                    'return_msg': 'A new project with the ID %s has been successfully created.' % new_project_id
                    }), 201  # Created


@app.route('/snape/1.0/projects/<string:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Synopsis:
        Deletes a project inside the system. This includes
        1. the database directory
        2. all tokens registered on the project
        This function claims the *shelve.lock* and the *db.lock* system locks.
    Status Codes:
        200: successful
        400: password or token count not found in request
        403: password invalid
        404: project with given ID not found
    :param project_id: unique project ID
    :returns response: JSON-object containing
        1. ID of deleted project
        2. return message
    """
    if not request.json or 'password' not in request.json:
        abort(400)  # Bad request
    if not server_password_is_valid(request.json['password']):
        abort(403)  # Forbidden
    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found
    db.delete_project(project_id = project_id)

    with open(os.path.join('shelve.lock'), 'a', 0) as shelve_lock:
        plocker.lock(shelve_lock, plocker.LOCK_EX)
        token_file = shelve.open('token_list')
        try:
            del token_file[str(project_id)]
        finally:
            token_file.close()

    return jsonify({'deleted_project_id': project_id,
                    'return_msg': 'The project with the ID %s has been successfully deleted.' % project_id
                    }), 200


@app.route('/snape/1.0/projects/<string:project_id>/tokens', methods=['POST'])
def add_new_tokens(project_id):
    """
    Synopsis:
        Generates new user tokens for a given project.
        This function claims the *shelve.lock* system lock.
    Status Codes:
        201: successful
        400: password or token count not found in request
        403: password invalid
        404: project with given ID not found
        413: too many tokens requested
    :param project_id: unique project ID
    :returns response: JSON-object containing
        1. set of new generated valid user tokens
        2. return message
    """
    if not request.json or 'password' not in request.json or 'token_count' not in request.json or \
            not is_int_castable(request.json['token_count']):
        abort(400)  # Bad request

    if not server_password_is_valid(request.json['password']):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found

    if int(request.json['token_count']) > TOKEN_MAX_REQUEST:
        abort(413)  # Payload too large

    token_file = shelve.open('token_list')
    new_tokens = []

    with open(os.path.join('shelve.lock'), 'a', 0) as shelve_lock:
        plocker.lock(shelve_lock, plocker.LOCK_EX)
        try:
            token_list = token_file['token_list']
            while len(new_tokens) < int(request.json['token_count']):
                new_token = generate_token(token_list)
                new_tokens.append(new_token)
                token_list.append(new_token)
            token_file['token_list'] = token_list
            token_file[str(project_id)] = token_file[str(project_id)] + new_tokens
        finally:
            token_file.close()

    return jsonify({'generated_tokens': new_tokens,
                    'return_msg': '%i new tokens have successfully been added to the '
                                  'project with the ID %s.' % (int(request.json['token_count']), project_id)
                    }), 201  # Created


@app.route('/snape/1.0/projects/<string:project_id>/tokens', methods=['DELETE'])
def remove_tokens(project_id):
    """
    Synopsis:
        Invalidates user tokens for a given project.
        This function claims the *shelve.lock* system lock.
    Status Codes:
        200: successful
        400: password or token count not found in request
        403: password invalid
        404: project with given ID not found
    :param project_id: unique project ID
    :returns response: JSON-object containing
        1. return message
    """
    if not request.json or 'password' not in request.json or 'tokens_to_delete' not in request.json:
        abort(400)  # Bad request
    if not server_password_is_valid(request.json['password']):
        abort(403)  # Forbidden
    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found

    with open(os.path.join('shelve.lock'), 'a', 0) as shelve_lock:
        plocker.lock(shelve_lock, plocker.LOCK_EX)
        token_file = shelve.open('token_list')
        try:
            token_file[str(project_id)] = filter(lambda x: x not in request.json['tokens_to_delete'],
                                                 token_file[str(project_id)])
        finally:
            token_file.close()

    return jsonify({'return_msg': 'The tokens have successfully been deleted from the '
                                  'project with the ID %s.' % project_id
                    }), 200  # OK


@app.route('/snape/1.0/projects/<string:project_id>/revisions/<string:token>', methods=['POST'])
def create_new_revision(project_id, token):
    """
    Synopsis:
        Checks in a new model revision into a given project.
        The model is saved as new file in the database.
        The project statistics are updated.
        This operation invalidates the project cache.
        This function claims the *db.lock* and *cache.lock* system locks.
    Status Codes:
        201: successful
        400: password or token count not found in request
        403: password invalid
        413: provided model file too large
        415: provided file has unsupported type
        422: model does not contain any parsable information
    :param project_id: unique project ID
    :param token: user authentification token
    :returns response: JSON-object containing
        1. new revision ID
        2. project ID
        3. return message
    """
    if request.content_length > MDJ_MAX_SIZE:
        abort(413)  # Payload Too Large

    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    model_file = None
    unicode_filename = ''

    if request.files and request.files['file'] and request.form['filename']:
        model_file = list()
        for line in request.files['file'].stream:
            model_file.append(line)
        escaped_filename = request.form['filename'].encode('utf-8')
        unescaped_filename = escaped_filename.decode('string-escape')
        unicode_filename = unescaped_filename.decode('utf-8')
    else:
        abort(400)  # Bad request

    if model_file is None or not allowed_file(unicode_filename):
        abort(415)  # Unsupported Media Type

    db.invalidate_cache(project_id)

    db.add_revision(project_id = 'temp', model_file = model_file, filename = unicode_filename)
    new_version_number = -1
    mdjs = db.get_project_models(project_id = 'temp')

    parsed = parser.parse_models(mdj_array = mdjs)
    db.delete_project('temp')
    if len(anal.get_diagram_names_and_ids(parsed)) == 0:
        abort(422)  # Unprocessable Entity

    else:
        new_version_number = db.add_revision(project_id = project_id, model_file = model_file,
                                             filename = unicode_filename)

    generate_statistics(project_id)

    return jsonify({'new_revision_id': new_version_number,
                    'project_id': project_id,
                    'return_msg': 'The new revision numbered %i has successfully been added to the project '
                                  'with the ID %s' % (new_version_number, project_id)
                    }), 201  # Created


@app.route('/snape/1.0/projects/<string:project_id>/revisions/<int:revision_id>/<string:token>', methods=['DELETE'])
def delete_revision(project_id, revision_id, token):
    """
    Synopsis:
        Deletes a checked in model from a given project.
        The project statistics are updated.
        This operation invalidates the project cache.
        This function claims the *db.lock* and *cache.lock* system locks.
    Status Codes:
        200: successful
        400: password or token count not found in request
        403: password invalid
        404: project not found in database
    :param project_id: unique project ID
    :param revision_id: ID of model revision to be deleted
    :param token: user authentification token
    :returns response: JSON-object containing
        1. new revision ID
        2. project ID
        3. return message
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id = project_id) or \
            not db.check_revision_exits(project_id = project_id, revision_id = revision_id):
        abort(404)  # Not found

    db.invalidate_cache(project_id)
    db.delete_revision(project_id = project_id, version_number = revision_id)

    generate_statistics(project_id)

    return jsonify({'deleted_revision_id': revision_id,
                    'project_id': project_id,
                    'return_msg': 'The revision numbered %i has successfully been removed '
                                  'from the project.' % revision_id
                    }), 200  # OK


@app.route('/snape/1.0/projects/<string:project_id>/diagrams/<string:token>', methods=['GET'])
def get_diagrams(project_id, token):
    """
    Synopsis:
        Collects and returns the diagram IDs contained in a project.
    Status Codes:
        200: successful
        400: password or token count not found in request
        403: password invalid
        404: project not found in database
        410: project is empty
    :param project_id: unique project ID
    :param token: user authentification token
    :returns response: JSON-object containing
        1. list of (name, ID) tuples
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found

    mdjs = db.get_project_models(project_id = project_id)
    if len(mdjs) < 1:
        abort(410)  # Gone

    parsed = parser.parse_models(mdj_array = mdjs)

    return jsonify({'dia_name_id_pairs': list(set(anal.get_diagram_names_and_ids(parsed)))
                    }), 200  # OK


@app.route('/snape/1.0/projects/<string:project_id>/history/<string:diagram_id>/<int:frame>/<string:token>',
           methods=['GET'])
def get_history(project_id, frame, token, diagram_id):
    """
    Synopsis:
        Returns a frame of the visualized diagram history of the given project.
        The frame is taken from the project cache. If no cache exists for the given diagram,
        all frames of the history are rendered and composed into a new cache.
        This function claims the *db.lock* and *cache.lock* system locks.
    Status Codes:
        400: invalid project ID
        403: password invalid
        404: project not found in database OR diagram ID not found in project
        410: project is empty
        416: frame index out of bounds
    :param project_id: unique project ID
    :param frame: index of frame to be returned. range: [0 - #revisions]
    :param token: user authentification token
    :param diagram_id: ID of diagram restricting which objects are to be rendered
    :returns file: file, mimetype = image/png
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found

    with open('cache.lock', 'a', 0) as cache_lock:
        plocker.lock(cache_lock, plocker.LOCK_EX)
        frame_path = db.get_cache_filepath(frame, project_id, diagram_id)
        if frame_path:
            return send_file(frame_path, mimetype = 'image/png')

        mdjs = db.get_project_models(project_id = project_id)
        if len(mdjs) == 0:
            abort(410)  # Gone
        if len(mdjs) < frame or frame < 0:
            abort(416)  # Range not acceptable

        parsed = parser.parse_models(mdj_array = mdjs)
        if not parsed:
            abort(500)  # Internal Server Error

        diagram_name_id_pairs = list(set(anal.get_diagram_names_and_ids(parsed)))
        if diagram_id not in map(lambda x: x[1], diagram_name_id_pairs):
            abort(404)  # Not found

        timeslice_array, error_flag = anal.get_timeslices(parsed = parsed, diagram_id = diagram_id)
        if error_flag:
            abort(500)  # Internal Server Error

        anim.render_timeslices(timeslice_array = timeslice_array)

        db.build_cache(project_id, diagram_id)

        frame_path = db.get_cache_filepath(frame, project_id, diagram_id)
        if frame_path:
            return send_file(frame_path, mimetype = 'image/png')
        else:
            abort(500)  # Internal Server Error


@app.route(
    '/snape/1.0/projects/<string:project_id>/changelog/<string:diagram_id>/<int:from_rev>/<int:to_rev>/<string:token>',
    methods=['GET'])
def get_recent_changes(project_id, from_rev, to_rev, token, diagram_id):
    """
    Synopsis:
        Returns a textual diff-log of the given project, restricted to objects in the given diagram.
        This function claims the *db.lock* system lock.
    Status Codes:
        400: invalid project ID
        403: password invalid
        404: project not found in database OR diagram ID not found in project
        410: project is empty
    :param project_id: unique project ID
    :param from_rev: revision index to start changelog
    :param to_rev: revision index to end changelog
    :param token: user authentification token
    :param diagram_id: ID of diagram restricting which objects are to be rendered
    :returns log: string
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found

    mdjs = db.get_project_models(project_id = project_id)
    if not mdjs:
        abort(410)  # Gone

    parsed = parser.parse_models(mdj_array = mdjs)
    if not parsed:
        abort(500)  # Internal Server Error

    diagram_name_id_pairs = list(set(anal.get_diagram_names_and_ids(parsed)))
    if diagram_id not in map(lambda x: x[1], diagram_name_id_pairs):
        abort(404)  # Not found

    timeslice_array, error_flag = anal.get_timeslices(parsed = parsed, diagram_id = diagram_id)

    if error_flag:
        abort(500)  # Internal Server Error

    log = gen.generate_log(timeslice_array = timeslice_array,
                           from_version = from_rev, to_version = to_rev)

    return log


@app.route('/snape/1.0/projects/<string:project_id>/info/<string:token>', methods=['GET'])
def project_info(project_id, token):
    """
    Synopsis:
        Returns information about the specified project.
        This function claims the *db.lock* system lock.
    Status Codes:
        200: success
        400: invalid project ID
        403: password invalid
        404: project not found in database
        410: project is empty
    :param project_id: unique project ID
    :param token: user authentification token
    :returns response: JSON-object containing
        1. list of project revision IDs
        2. project ID
        3. list of revision metadata
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id = project_id):
        abort(404)  # Not found

    project_model_ids, model_metadata = db.get_project_info(project_id)
    if not project_model_ids:
        abort(410)  # Gone

    return jsonify({'project_versions': project_model_ids,
                    'project_id': project_id,
                    'model_metadata': model_metadata
                    }), 200


@app.route('/snape/1.0/projects/<string:project_id>/revisions/<int:revision_id>/download/<string:token>')
def download_revision(project_id, revision_id, token):
    """
    Synopsis:
        Provides an uploaded revision as download.
        This function claims the *db.lock* system lock.
    Status Codes:
        400: invalid project ID
        403: password invalid
        404: project not found in database OR revision not found in database
    :param project_id: unique project ID
    :param revision_id: ID of the revision to be downloaded
    :param token: user authentification token
    :returns file: file
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    if not db.check_project_exists(project_id):
        abort(404)  # Not found

    mdjs = db.get_project_models(project_id = project_id)
    if not mdjs:
        abort(404)  # Not found

    for path in mdjs:
        if 'v' + str(revision_id) in path:
            break
    else:
        abort(404)  # Not found

    return send_file(path, as_attachment = True, attachment_filename = path.split(os.path.sep)[-1])


@app.route('/snape/1.0/projects/<string:project_id>/statistics/<string:stat_type>/<string:token>')
def get_statistics(project_id, stat_type, token):
    """
    Synopsis:
        Provides an image containing statistics about a specific project.
        This function claims the *db.lock* system lock.
    Status Codes:
        400: invalid project ID
        403: password invalid
        404: project not found in database OR revision not found in database
    :param project_id: unique project ID
    :param stat_type: statistics type to be returned
    :param token: user authentification token
    :returns file: file, mimetype = image/png
    """
    if not is_int_castable(project_id):
        abort(400)  # Bad request

    if not token_is_valid(project_id, token):
        abort(403)  # Forbidden

    stats = db.get_project_statistics(project_id)

    reply = list(filter(lambda x: stat_type in x, stats))
    if len(reply) == 0:
        abort(404)  # Not found

    return send_file(reply[0], mimetype = 'image/png')


@app.route('/shutdown', methods=['POST'])
def __shutdown():
    """
    Synopsis:
        Initiates server shutdown.
    """
    if not request.json or 'password' not in request.json:
        abort(400)  # Bad request
    if not shutdown_password_is_valid(request.json['password']):
        abort(403)  # Forbidden
    __shutdown_server()
    print('Server shutting down...')


def start_web_service(host = '127.0.0.1', port = 20030, debug = False):
    """
    Synopsis:
        Starts web service.
        This function claims the *cache.lock* system lock.
    :param host: host-IP
    :param port: port number
    :param debug: if True, live code updates are enabled
    """
    app.debug = debug
    os.chdir(ROOT)

    if not os.path.isfile('cache.lock'):
        with open('cache.lock', 'a'):
            pass

    if not os.path.isfile(os.path.join('database', 'cache.lock')):
        with open(os.path.join('database', 'db.lock'), 'a'):
            pass

    assert os.access('cache.lock', os.W_OK), 'Could not start SNAPE due to missing permissions'
    assert os.access(os.path.join('database', 'db.lock'), os.W_OK), 'Could not start SNAPE due to missing permissions'

    with open('cache.lock', 'a', 0) as cache_lock:
        plocker.lock(cache_lock, plocker.LOCK_EX)
        if not os.path.isfile('id_counter'):
            c = shelve.open('id_counter')
            c['counter'] = 1
            c.close()

        if not os.path.isfile('token_list'):
            c = shelve.open('token_list')
            c['token_list'] = []
            c.close()

    assert os.access('id_counter', os.W_OK), 'Could not start SNAPE due to missing permissions'
    assert os.access('token_list', os.W_OK), 'Could not start SNAPE due to missing permissions'

    app.config['PROPAGATE_EXCEPTIONS'] = True

    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        try:
            if not os.path.isdir('logs'):
                os.makedirs('logs')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
            log_target = os.path.join('logs', 'error.log')

            handler = RotatingFileHandler(filename = log_target, mode = 'a', maxBytes = 3e6,
                                          backupCount = 2, encoding = None, delay = 0)
            handler.setFormatter(formatter)
            handler.setLevel(logging.NOTSET)

            logger = logging.getLogger()
            logger.setLevel(logging.NOTSET)
            logger.addHandler(handler)
            logging.info('\n' + '-' * 80 + '\n')
        except Exception:
            print('Failed to setup logging. Does SNAPE have writing permission?')

    try:
        if USE_SSL:
            ssl_context = (CRT_PATH, KEY_PATH)
            app.run(host = host, port = port, debug = debug, ssl_context = ssl_context)
        else:
            app.run(host = host, port = port, debug = debug)
    except socket.error:
        print 'Could not start SNAPE service with given settings. Maybe your specified port (%i) is already in use?' \
              % port


def __shutdown_server():
    """
    Synopsis:
        Shuts down server.
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if not func:
        raise RuntimeError('Not running using Werkzeug Server')
    func()


@app.route('/api', methods=['GET'])
def serve_api():
    return send_file('api/swagger.json', mimetype = 'application/json')


if __name__ == '__main__':
    pass
