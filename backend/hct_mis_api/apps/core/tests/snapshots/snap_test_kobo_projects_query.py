# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestKoboProjectsQuery::test_all_kobo_projects_query 1'] = {
    'data': {
        'allKoboProjects': {
            'edges': [
                {
                    'node': {
                        'country': 'Afghanistan',
                        'dateModified': '2020-05-20T10:44:19.596582+00:00',
                        'deploymentActive': False,
                        'hasDeployment': False,
                        'name': 'cloned test',
                        'uid': 'a7rujYsuzrMo7PJtriSfqK',
                        'xlsLink': 'https://kobo.humanitarianresponse.info/api/v2/assets/a7rujYsuzrMo7PJtriSfqK/?format=json.xls'
                    }
                },
                {
                    'node': {
                        'country': 'Afghanistan',
                        'dateModified': '2020-05-20T10:44:19.417452+00:00',
                        'deploymentActive': False,
                        'hasDeployment': False,
                        'name': 'cloned test',
                        'uid': 'aNZohcKTvCTg2tRpKGYC4E',
                        'xlsLink': 'https://kobo.humanitarianresponse.info/api/v2/assets/aNZohcKTvCTg2tRpKGYC4E/?format=json.xls'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['TestKoboProjectsQuery::test_single_kobo_project_query 1'] = {
    'data': {
        'koboProject': {
            'country': 'Afghanistan',
            'dateModified': '2020-05-20T10:44:19.596582+00:00',
            'deploymentActive': False,
            'hasDeployment': False,
            'name': 'cloned test',
            'uid': 'a7rujYsuzrMo7PJtriSfqK',
            'xlsLink': 'https://kobo.humanitarianresponse.info/api/v2/assets/a7rujYsuzrMo7PJtriSfqK/?format=json.xls'
        }
    }
}
