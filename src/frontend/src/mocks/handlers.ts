import { http, HttpResponse } from 'msw';
import { restProfileRetrieve } from './responses/restProfileRetrieve';

export const handlers = [
  //restProfileRetrieve
  http.get('http://localhost:3000/api/rest/profile/', () => {
    return HttpResponse.json(restProfileRetrieve);
  }),
];
