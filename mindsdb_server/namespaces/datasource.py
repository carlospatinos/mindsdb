import os
import time
import datetime
from flask import request, send_file
from flask_restplus import Resource, fields

from mindsdb_server.namespaces.configs.datasources import ns_conf
from mindsdb_server.namespaces.entitites.datasources.datasource import (
    datasource_metadata,
    put_datasource_params,
    post_datasource_params,
    EXAMPLES as DATASOURCES_LIST_EXAMPLE
)
from mindsdb_server.namespaces.entitites.datasources.datasource_data import (
    get_datasource_rows_params,
    datasource_rows_metadata,
    EXAMPLES as GET_DATASOURCE_ROWS_EXAMPLES
)
from mindsdb_server.namespaces.entitites.datasources.datasource_files import (
    put_datasource_file_params
)
from mindsdb_server.namespaces.entitites.datasources.datasource_missed_files import (
    datasource_missed_files_metadata,
    get_datasource_missed_files_params,
    EXAMPLES as GET_DATASOURCE_MISSED_FILES_EXAMPLES
)

FILES_PATH = 'uploads'

@ns_conf.route('/')
class DatasourcesList(Resource):
    @ns_conf.doc('get_atasources_list')
    @ns_conf.marshal_list_with(datasource_metadata)
    def get(self):
        '''List all datasources'''
        return DATASOURCES_LIST_EXAMPLE

@ns_conf.route('/<name>')
@ns_conf.param('name', 'Datasource name')
class Datasource(Resource):
    @ns_conf.doc('get_datasource')
    @ns_conf.marshal_with(datasource_metadata)
    def get(self, name):
        '''return datasource metadata'''
        return DATASOURCES_LIST_EXAMPLE[0]

    @ns_conf.doc('post_datasource', params=post_datasource_params)
    def post(self, name):
        '''update datasource attributes'''
        return '', 200

    @ns_conf.doc('delete_datasource')
    def delete(self, name):
        '''delete datasource'''
        to_del = ([x for x in DATASOURCES_LIST_EXAMPLE if x['name'] == name] or [None])[0]
        if to_del:
            DATASOURCES_LIST_EXAMPLE.remove(to_del)
            return '', 200
        return '', 404

    @ns_conf.doc('put_datasource', params=put_datasource_params)
    @ns_conf.marshal_with(datasource_metadata)
    def put(self, name):
        '''add new datasource'''
        # request.json - for regular put
        # request.values - for multipart form data
        data = request.json or request.values
        
        datasource_name = data['name']
        datasource_type = data['sourceType']
        datasource_source = data['source']

        names = [x['name'] for x in DATASOURCES_LIST_EXAMPLE]
        if datasource_name in names:
            datasource_name += '(1)'

        if datasource_type == 'file':
            datasource_file = request.files['file']
            if not os.path.exists(FILES_PATH):
                os.mkdir(FILES_PATH)
            path = os.path.join(FILES_PATH, datasource_source)
            open(path, 'wb').write(datasource_file.read())

        DATASOURCES_LIST_EXAMPLE.append({
            'name': datasource_name,
            'source_type': datasource_type,
            'source': datasource_source,
            'missed_files': False,
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'row_count': 0,
            'columns': [{
                'name': 'name',
                'type': 'string'
            }, {
                'name': 'rental_price',
                'type': 'number'
            }]
        })

        time.sleep(1.0)
        return DATASOURCES_LIST_EXAMPLE[-1]

@ns_conf.route('/<name>/data/')
@ns_conf.param('name', 'Datasource name')
class DatasourceData(Resource):
    @ns_conf.doc('get_datasource_data', params=get_datasource_rows_params)
    @ns_conf.marshal_with(datasource_rows_metadata)
    def get(self, name):
        '''return data rows'''
        return GET_DATASOURCE_ROWS_EXAMPLES[0]

@ns_conf.route('/<name>/files/<column_name>:<index>')
@ns_conf.param('name', 'Datasource name')
@ns_conf.param('column_name', 'column name')
@ns_conf.param('index', 'row index')
class DatasourceFiles(Resource):
    @ns_conf.doc('put_datasource_file', params=put_datasource_file_params)
    def put(self, name):
        '''put file'''
        return '', 200

@ns_conf.route('/<name>/missed_files')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFiles(Resource):
    @ns_conf.doc('get_datasource_missed_files', params=get_datasource_missed_files_params)
    @ns_conf.marshal_with(datasource_missed_files_metadata)
    def get(self, name):
        '''return missed files'''
        return GET_DATASOURCE_MISSED_FILES_EXAMPLES[0]


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFiles(Resource):
    @ns_conf.doc('get_datasource_download')
    def get(self, name):
        '''download uploaded file'''
        ds = ([x for x in DATASOURCES_LIST_EXAMPLE if x['name'] == name] or [None])[0]
        if not ds:
            return '', 404
        path = os.path.join(FILES_PATH, ds['source'])
        if not os.path.exists(path):
            return '', 404

        return send_file(path, as_attachment=True)
