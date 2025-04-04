import { api, handleApiResponse } from './api';
// import { ProgramCreate } from '@restgenerated/models/ProgramCreate';

//TODO: Add generated types

interface Program {
  id: string;
  name: string;
  description: string;
  status: string;
  business_area: string;
  created_at: string;
  updated_at: string;
}

export const fetchProgram = async (
  businessArea: string,
  programId: string,
): Promise<Program> => {
  return handleApiResponse(api.get(`${businessArea}/programs/${programId}/`));
};

//TODO add types

// export const createProgram = async (
//   businessArea: string,
//   body: ProgramCreate,
// ): Promise<ProgramCreateResponse> => {
//   return postRequest<ProgramCreateResponse>(
//     `${businessArea}/program/create/`,
//     body,
//     'create program',
//   );
// };

//TODO: Add generated types
interface ProgramsParams {
  active?: boolean;
  business_area?: string;
  limit?: number;
  offset?: number;
  ordering?: string;
  status?: 'ACTIVE' | 'DRAFT' | 'FINISHED';
  updated_at_after?: string;
  updated_at_before?: string;
}

interface Program {
  // Define the properties of a Program here
}

interface PaginatedListResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export const fetchPrograms = async (
  params: ProgramsParams,
): Promise<PaginatedListResponse<Program>> => {
  const queryString = new URLSearchParams(params as any).toString();
  return handleApiResponse(api.get(`/api/rest/programs/?${queryString}`));
};
