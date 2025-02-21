import { api, handleApiResponse } from './api';
import { Program } from '@restgenerated/models/Program';
// import { ProgramCreate } from '@restgenerated/models/ProgramCreate';

//TODO: Add generated types
interface BeneficiaryGroup {
  id: string;
  name: string;
  group_label: string;
  group_label_plural: string;
  member_label: string;
  member_label_plural: string;
  master_detail: boolean;
}

export interface PaginatedListResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export const fetchBeneficiaryGroups = async (): Promise<
  PaginatedListResponse<BeneficiaryGroup>
> => {
  return handleApiResponse(api.get('beneficiary-groups/'));
};

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
