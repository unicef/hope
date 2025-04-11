import { http, HttpResponse } from 'msw';
import { restUsersProfileRetrieve } from './responses/restUsersProfileRetrieve';
import { restBeneficiaryGroupsList } from './responses/restBeneficiaryGroupsList';
import { restBusinessAreasHouseholdsList } from './responses/restBusinessAreasHouseholdsList';
import { restBusinessAreasProgramsHouseholdsList } from './responses/restBusinessAreasProgramsHouseholdsList';
import { restBusinessAreasProgramsHouseholdsRetrieve } from './responses/restBusinessAreasProgramsHouseholdsRetrieve';
import { restBusinessAreasProgramsPeriodicFieldsList } from './responses/restBusinessAreasProgramsPeriodicFieldsList';
import { restBusinessAreasProgramsPeriodicDataUpdateTemplatesList } from './responses/restBusinessAreasProgramsPeriodicDataUpdateTemplatesList';
import { restBusinessAreasProgramsPeriodicDataUpdateUploadsList } from './responses/restBusinessAreasProgramsPeriodicDataUpdateUploadsList';
import { restBusinessAreasProgramsPeriodicDataUpdateTemplatesRetrieve } from './responses/restBusinessAreasProgramsPeriodicDataUpdateTemplatesRetrieve';
import { restBusinessAreasProgramsCyclesRetrieve } from './responses/restBusinessAreasProgramsCyclesRetrieve';

const baseUrl = 'http://localhost:3000/api/rest/business-areas/';

const endpoints = [
  {
    url: 'http://localhost:3000/api/rest/users/profile/',
    response: restUsersProfileRetrieve,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/cycles/:id/`,
    response: restBusinessAreasProgramsCyclesRetrieve,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/periodic-fields/`,
    response: restBusinessAreasProgramsPeriodicFieldsList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/periodic-data-update-templates/`,
    response: restBusinessAreasProgramsPeriodicDataUpdateTemplatesList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/periodic-data-update-uploads/`,
    response: restBusinessAreasProgramsPeriodicDataUpdateUploadsList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/periodic-data-update-templates/:id/`,
    response: restBusinessAreasProgramsPeriodicDataUpdateTemplatesRetrieve,
  },
  {
    url: '/api/rest/beneficiary-groups/',
    response: restBeneficiaryGroupsList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/households/`,
    response: restBusinessAreasProgramsHouseholdsList,
  },
  {
    url: `${baseUrl}:business_area_slug/households/`,
    response: restBusinessAreasHouseholdsList,
  },
  {
    url: `${baseUrl}:business_area_slug/programs/:program_slug/households/:id/`,
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
