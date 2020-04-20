# encoding=utf8

import logging
import logging.config
import yaml

with open('logging.yml') as cfg:
    logging.config.dictConfig(yaml.safe_load(cfg))

logger = logging.getLogger()

from doit import get_var
from roald import Roald
import data_ub_tasks

config = {
    'dumps_dir': get_var('dumps_dir', '/opt/data.ub/www/default/dumps'),
    'dumps_dir_url': get_var('dumps_dir_url', 'http://data.ub.uio.no/dumps'),
    'graph': 'http://data.ub.uio.no/humord',
    'fuseki': 'http://localhost:3031/ds',
    'basename': 'humord',
    'git_user': 'ubo-bot',
    'git_email': 'danmichaelo+ubobot@gmail.com',
    'es_index': 'authority'
}

DOIT_CONFIG = {
    'default_tasks': [
        'git-push',
        'publish-dumps',
        'fuseki',
    ]
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
            'remote': 'https://rawgit.com/scriptotek/data_ub_ontology/master/ub-onto.ttl',
             'local': 'src/ub-onto.ttl'
        }
    ]:
        yield data_ub_tasks.fetch_remote_gen(file['remote'], file['local'], ['fetch_core:git-pull'])


def task_fetch_extras():

    yield {
        'doc': 'Fetch remote extra files that have changed',
        'basename': 'fetch-extras',
        'name': None
    }
    for file in [
        {'remote': 'https://lambda.biblionaut.net/export/real_hume_mappings.ttl',
            'local': 'src/real_hume_mappings.ttl'},
        {'remote': 'https://lambda.biblionaut.net/export/ccmapper_mappings.ttl',
            'local': 'src/ccmapper_mappings.ttl'},
    ]:
        yield data_ub_tasks.fetch_remote_gen(file['remote'], file['local'], [])


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
        #     'created_by': 'NO-TrBIB',
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
        'actions': [
            'mkdir -p dist',
            build
        ],
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
        roald.set_uri_format('http://data.ub.uio.no/%s/c{id}' % config['basename'], 'HUME')

        # 1) MARC21 for Alma and general use
        marc21options = {
            'vocabulary_code': 'humord',
            'created_by': 'NO-TrBIB',
            'include_d9': 'simple',
            'include_memberships': True,
        }
        roald.export('dist/%s.marc21.xml' %
                     config['basename'], format='marc21', **marc21options)
        logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # ------------------------------------------------------------------------------

        roald.load('src/real_hume_mappings.ttl', format='skos')

        # 1) MARC21 with $9 fields for CCMapper
        marc21options = {
            'vocabulary_code': 'humord',
            'created_by': 'NO-TrBIB',
            'include_d9': 'complex',
            'include_memberships': True,
        }
        roald.export('dist/%s.ccmapper.marc21.xml' %
                     config['basename'], format='marc21',
                     **marc21options)
        logger.info('Wrote dist/%s.ccmapper.marc21.xml', config['basename'])

        # ------------------------------------------------------------------------------

        roald.load('src/ccmapper_mappings.ttl', format='skos')

        # 3) RDF (core + mappings)
        prepared = roald.prepare_export(format='rdfskos',
            include=[
                '%s.scheme.ttl' % config['basename'],
                'src/ub-onto.ttl'
            ],
            with_ccmapper_candidates=True,
            infer=True
        )
        prepared.write('dist/%s.complete.ttl' % config['basename'], format='turtle')
        logger.info('Wrote dist/%s.complete.ttl', config['basename'])
        prepared.write('dist/%s.complete.nt' % config['basename'], format='nt')
        logger.info('Wrote dist/%s.complete.nt', config['basename'])

    return {
        'doc': 'Build distribution files (RDF/SKOS + MARC21XML) from source files',
        'basename': 'build-extras',
        'actions': [
            'mkdir -p dist',
            build,
        ],
        'file_dep': [
            'src/humord.xml',
            'src/real_hume_mappings.ttl',
            'src/ccmapper_mappings.ttl',
            'src/ub-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            'dist/%s.marc21.xml' % config['basename'],
            'dist/%s.ccmapper.marc21.xml' % config['basename'],
            'dist/%s.complete.ttl' % config['basename'],
            'dist/%s.complete.nt' % config['basename'],
        ]
    }


def task_build_mappings():
    src_uri = 'http://data.ub.uio.no/humord/'
    mapping_sets = [
        {
            'source_files': ['src/real_hume_mappings.ttl'],
            'target': 'realfagstermer',
        },
        {
            'source_files': ['src/ccmapper_mappings.ttl'],
            'target': 'ddc23no',
        },
    ]

    yield {
        'doc': 'Build mapping distributions',
        'basename': 'build-mappings',
        'name': None
    }

    for mapping_set in mapping_sets:
        yield data_ub_tasks.build_mappings_gen(
            mapping_set['source_files'],
            'dist/%s-%s.mappings.nt' % (config['basename'], mapping_set['target']),
            src_uri
        )

def task_build_json():
    return data_ub_tasks.gen_solr_json(config, 'humord')


def task_git_push():
    return data_ub_tasks.git_push_task_gen(config)


def task_publish_dumps():
    return data_ub_tasks.publish_dumps_task_gen(config['dumps_dir'], [
        '%s.marc21.xml' % config['basename'],
        '%s.ccmapper.marc21.xml' % config['basename'],
        '%s.ttl' % config['basename'],
        '%s.complete.ttl' % config['basename'],
        '%s.complete.nt' % config['basename'],
        '%s-realfagstermer.mappings.nt' % config['basename'],
        '%s-ddc23no.mappings.nt' % config['basename'],
    ])


def task_fuseki():
    return data_ub_tasks.fuseki_task_gen(config, ['dist/%(basename)s.complete.ttl'])


def task_elasticsearch():
    return data_ub_tasks.gen_elasticsearch(config, 'humord')
