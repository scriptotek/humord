# encoding=utf8
from doit import get_var
from roald import Roald

import logging
import logging.config
logging.config.fileConfig('logging.cfg', )
logger = logging.getLogger(__name__)

import data_ub_tasks

config = {
    'dumps_dir': get_var('dumps_dir', '/opt/data.ub/www/default/dumps'),
    'dumps_dir_url': get_var('dumps_dir_url', 'http://data.ub.uio.no/dumps'),
    'graph': 'http://data.ub.uio.no/humord',
    'fuseki': 'http://localhost:3031/ds',
    'basename': 'humord',
    'git_user': 'ubo-bot',
    'git_email': 'danmichaelo+ubobot@gmail.com',
}


def task_fetch_core():

    yield {
        'doc': 'Fetch remote core files that have changed',
        'basename': 'fetch-core',
        'name': None
    }
    yield data_ub_tasks.git_pull_task_gen(config)
    for file in [
        {
            'remote': 'http://www.bibsys.no/files/out/humordsok/HUMEregister.xml',
             'local': 'src/humord.xml'
        },
        {
            'remote': 'https://rawgit.com/scriptotek/data_ub_ontology/master/ub-onto.ttl',
             'local': 'src/ub-onto.ttl'
        }
    ]:
        yield {
            'name': file['local'],
            'actions': [(data_ub_tasks.fetch_remote, [], {
                'remote': file['remote'],
                'etag_cache': '{}.etag'.format(file['local'])
            })],
            'task_dep': ['fetch_core:git-pull'],
            'targets': [file['local']]
        }


def task_fetch_extras():

    yield {
        'doc': 'Fetch remote extra files that have changed',
        'basename': 'fetch-extras',
        'name': None
    }
    for file in [
        {
            'remote': 'https://lambda.biblionaut.net/export.rdf',
             'local': 'src/lambda.rdf'
        }
    ]:
        yield {
            'name': file['local'],
            'actions': [(data_ub_tasks.fetch_remote, [], {
                'remote': file['remote'],
                'etag_cache': '{}.etag'.format(file['local'])
            })],
            'targets': [file['local']]
        }


def task_build_core():

    def build(task):
        logger.info('Building new core dist')
        roald = Roald()
        roald.load('src/humord.xml', format='bibsys', language='nb')
        roald.set_uri_format(
            'http://data.ub.uio.no/%s/c{id}' % config['basename'])
        roald.save('%s.json' % config['basename'])
        logger.info('Wrote %s.json', config['basename'])

        includes = [
            '%s.scheme.ttl' % config['basename'],
            'src/ub-onto.ttl'
        ]

        # 1) MARC21
        # marc21options = {
        #     'vocabulary_code': 'humord',
        #     'created_by': 'No-TrBIB',
        #     'mappings_from': ['src/lambda.rdf']
        # }
        # roald.export('dist/%s.marc21.xml' %
        #              config['basename'], format='marc21', **marc21options)
        # logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # 2) RDF (core)
        roald.export('dist/%s.ttl' % config['basename'],
                     format='rdfskos',
                     include=includes
                     )
        logger.info('Wrote dist/%s.core.ttl', config['basename'])

    return {
        'doc': 'Build distribution files (RDF/SKOS + MARC21XML) from source files',
        'basename': 'build-core',
        'actions': [build],
        'file_dep': [
            'src/humord.xml',
            'src/ub-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            '%s.json' % config['basename'],
            'dist/%s.ttl' % config['basename'],
        ]
    }


def task_build_extras():

    def build(task):
        logger.info('Building extras')
        roald = Roald()
        roald.load('src/humord.xml', format='bibsys', language='nb')
        roald.set_uri_format(
            'http://data.ub.uio.no/%s/c{id}' % config['basename'])
        logger.info('Wrote %s.json', config['basename'])

        includes = [
            '%s.scheme.ttl' % config['basename'],
            'src/ub-onto.ttl'
        ]

        mappings = [
            'src/lambda.rdf'
        ]

        # 1) MARC21
        marc21options = {
            'vocabulary_code': 'humord',
            'created_by': 'No-TrBIB',
            'mappings_from': ['src/lambda.rdf']
        }
        roald.export('dist/%s.marc21.xml' %
                     config['basename'], format='marc21', **marc21options)
        logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # 3) RDF (core + mappings)
        roald.export('dist/%s.complete.ttl' % config['basename'],
                     format='rdfskos',
                     include=includes,
                     mappings_from=mappings
                     )
        logger.info('Wrote dist/%s.complete.ttl', config['basename'])

    return {
        'doc': 'Build distribution files (RDF/SKOS + MARC21XML) from source files',
        'basename': 'build-extras',
        'actions': [build],
        'file_dep': [
            'src/humord.xml',
            'src/lambda.rdf',
            'src/ub-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            'dist/%s.marc21.xml' % config['basename'],
            'dist/%s.complete.ttl' % config['basename']
        ]
    }


def task_build_json():
    return data_ub_tasks.gen_solr_json(config, 'humord')


def task_git_push():
    return data_ub_tasks.git_push_task_gen(config)


def task_publish_dumps():
    return data_ub_tasks.publish_dumps_task_gen(config['dumps_dir'], [
        '%s.marc21.xml' % config['basename'],
        '%s.ttl' % config['basename'],
        '%s.complete.ttl' % config['basename']
    ])


def task_fuseki():
    return data_ub_tasks.fuseki_task_gen(config, ['dist/%(basename)s.complete.ttl'])
