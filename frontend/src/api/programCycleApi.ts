import { api } from '@api/api';

export interface ProgramCyclesQuery {
  ordering: string;
  limit?: number;
  offset?: number;
}

export interface PaginatedListResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export type ProgramCycleStatus = 'Active' | 'Draft' | 'Finished';

export interface ProgramCycle {
  id: string;
  unicef_id: string;
  title: string;
  status: ProgramCycleStatus;
  start_date: string;
  end_date: string;
  created_at: string;
  total_entitled_quantity_usd: number;
  total_undelivered_quantity_usd: number;
  total_delivered_quantity_usd: number;
}

export const fetchProgramCycles = async (
  businessArea: string,
  programId: string,
  query: ProgramCyclesQuery,
): Promise<PaginatedListResponse<ProgramCycle>> => {
  return api.get(`${businessArea}/programs/${programId}/cycles/`, query);
};
