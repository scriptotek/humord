# encoding=utf8
from doit import get_var
from roald import Roald

import logging
import logging.config
logging.config.fileConfig('logging.cfg', )
logger = logging.getLogger(__name__)

import data_ub_tasks

config = {
    'dumps_dir': get_var('dumps_dir', './dumps'),
    'graph': 'http://data.ub.uio.no/humord',
    'fuseki': 'http://localhost:3030/ds',
    'basename': 'humord'
}


def task_fetch():

    logger.info('Checking for updated files')

    yield {
        'doc': 'Fetch remote files that have changed',
        'basename': 'fetch',
        'name': None
    }
    yield {
        'name': 'git pull',
        'actions': [
            'git config user.name "ubo-bot"',
            'git config user.email "danmichaelo+ubobot@gmail.com"',
            'git pull',
        ]
    }
    for file in [
        {
            'remote': 'http://www.bibsys.no/files/out/humordsok/HUMEregister.xml',
             'local': 'src/humord.xml'
        },
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


def task_build():

    def build_dist(task):
        logger.info('Building new dist')
        roald = Roald()
        roald.load('src/humord.xml', format='bibsys', language='nb')
        roald.set_uri_format(
            'http://data.ub.uio.no/%s/c{id}' % config['basename'])
        roald.save('%s.json' % config['basename'])
        logger.info('Wrote %s.json', config['basename'])

        includes = [
            '%s.scheme.ttl' % config['basename'],
            'ubo-onto.ttl'
        ]

        mappings = [
            'src/lambda.rdf'
        ]

        # 1) MARC21
        marc21options = {
            'vocabulary_code': 'humord',
            'created_by': 'NoOU',
            'mappings_from': ['src/lambda.rdf']
        }
        roald.export('dist/%s.marc21.xml' %
                     config['basename'], format='marc21', **marc21options)
        logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # 2) RDF (core)
        roald.export('dist/%s.ttl' % config['basename'],
                     format='rdfskos',
                     include=includes
                     )
        logger.info('Wrote dist/%s.core.ttl', config['basename'])

        # 3) RDF (core + mappings)
        roald.export('dist/%s.complete.ttl' % config['basename'],
                     format='rdfskos',
                     include=includes,
                     mappings_from=mappings
                     )
        logger.info('Wrote dist/%s.complete.ttl', config['basename'])

    return {
        'doc': 'Build distribution files (RDF/SKOS + MARC21XML) from source files',
        'actions': [build_dist],
        'file_dep': [
            'src/humord.xml',
            'src/lambda.rdf',
            'ubo-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            '%s.json' % config['basename'],
            'dist/%s.marc21.xml' % config['basename'],
            'dist/%s.ttl' % config['basename'],
            'dist/%s.complete.ttl' % config['basename']
        ]
    }


# def task_git_push():
#     return data_ub_tasks.git_push_task_gen(config)


def task_publish_dumps():
    return data_ub_tasks.publish_dumps_task_gen(config['dumps_dir'], [
        '%s.marc21.xml' % config['basename'],
        '%s.ttl' % config['basename'],
        '%s.complete.ttl' % config['basename']
    ])


def task_fuseki():
    return data_ub_tasks.fuseki_task_gen(config)
