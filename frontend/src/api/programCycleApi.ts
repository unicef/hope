import { api } from '@api/api';

interface ProgramCyclesQuery {
  ordering: string;
  limit?: number;
  offset?: number;
}

export const fetchProgramCycles = async (
  businessArea: string,
  programId: string,
  query: ProgramCyclesQuery,
) => {
  return api.get(`${businessArea}/programs/${programId}/cycles/`, query);
};
