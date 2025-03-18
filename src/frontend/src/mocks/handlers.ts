import { http, HttpResponse } from 'msw';
import { restUsersProfileRetrieve } from './responses/restUsersProfileRetrieve';
import { restProgramsCyclesRetrieve } from './responses/restProgramsCyclesRetrieve';
import { restProgramsPeriodicDataUpdatePeriodicFieldsList } from './responses/restProgramsPeriodicDataUpdatePeriodicFieldsList';
import { restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList } from './responses/restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList';
import { restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList } from './responses/restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList';
import { restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve } from './responses/restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve';
import { restBeneficiaryGroupsList } from './responses/restBeneficiaryGroupsList';
import { restBusinessAreasHouseholdsList } from './responses/restBusinessAreasHouseholdsList';
import { restBusinessAreasProgramsHouseholdsList } from './responses/restBusinessAreasProgramsHouseholdsList';
import { restBusinessAreasProgramsHouseholdsRetrieve } from './responses/restBusinessAreasProgramsHouseholdsRetrieve';

const baseUrl = 'http://localhost:3000/api/rest/business-areas/';

const endpoints = [
  {
    url: 'http://localhost:3000/api/rest/profile/',
    response: restUsersProfileRetrieve,
  },
  {
    url: `${baseUrl}:business_area/programs/:program_id/cycles/:id/`,
    response: restProgramsCyclesRetrieve,
  },
  {
    url: `${baseUrl}:business_area/programs/:program_id/periodic-data-update/periodic-fields/`,
    response: restProgramsPeriodicDataUpdatePeriodicFieldsList,
  },
  {
    url: `${baseUrl}:business_area/programs/:program_id/periodic-data-update/periodic-data-update-templates/`,
    response: restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList,
  },
  {
    url: `${baseUrl}:business_area/programs/:program_id/periodic-data-update/periodic-data-update-uploads/`,
    response: restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList,
  },
  {
    url: `${baseUrl}:business_area/programs/:program_id/periodic-data-update/periodic-data-update-templates/:id/`,
    response: restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve,
  },
  {
    url: `${baseUrl}:business_area/beneficiary-groups/`,
    response: restBeneficiaryGroupsList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_programme_code/households/`,
    response: restBusinessAreasProgramsHouseholdsList,
  },
  {
    url: `${baseUrl}:business_area_slug/households/`,
    response: restBusinessAreasHouseholdsList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_programme_code/households/:id/`,
    response: restBusinessAreasProgramsHouseholdsRetrieve,
  },
];

const createGetHandler = (url: string, response: any) => {
  return http.get(url, () => {
    return HttpResponse.json(response);
  });
};

export const handlers = endpoints.map((endpoint) =>
  createGetHandler(endpoint.url, endpoint.response),
);
