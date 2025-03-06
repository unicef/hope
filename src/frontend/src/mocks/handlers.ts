import { http, HttpResponse } from 'msw';
import { restProfileRetrieve } from './responses/restProfileRetrieve';
import { restProgramsCyclesRetrieve } from './responses/restProgramsCyclesRetrieve';
import { restProgramsPeriodicDataUpdatePeriodicFieldsList } from './responses/restProgramsPeriodicDataUpdatePeriodicFieldsList';
import { restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList } from './responses/restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList';
import { restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList } from './responses/restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList';
import { restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve } from './responses/restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve';
import { restBeneficiaryGroupsList } from './responses/restBeneficiaryGroupsList';

const endpoints = [
  {
    url: 'http://localhost:3000/api/rest/profile/',
    response: restProfileRetrieve,
  },
  {
    url: 'http://localhost:3000/api/rest/:business_area/programs/:program_id/cycles/:id/',
    response: restProgramsCyclesRetrieve,
  },
  {
    url: 'http://localhost:3000/api/rest/:business_area/programs/:program_id/periodic-data-update/periodic-fields/',
    response: restProgramsPeriodicDataUpdatePeriodicFieldsList,
  },
  {
    url: 'http://localhost:3000/api/rest/:business_area/programs/:program_id/periodic-data-update/periodic-data-update-templates/',
    response: restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList,
  },
  {
    url: 'http://localhost:3000/api/rest/:business_area/programs/:program_id/periodic-data-update/periodic-data-update-uploads/',
    response: restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList,
  },
  {
    url: 'http://localhost:3000/api/rest/:business_area/programs/:program_id/periodic-data-update/periodic-data-update-templates/:id/',
    response: restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve,
},
{
  url: 'http://localhost:3000/api/rest/beneficiary-groups/',
  response: restBeneficiaryGroupsList,
},
];

const createGetHandler = (url: string, response: any) => {
  return http.get(url, () => {
    return HttpResponse.json(response);
  });
};

export const handlers = endpoints.map(endpoint => createGetHandler(endpoint.url, endpoint.response));
