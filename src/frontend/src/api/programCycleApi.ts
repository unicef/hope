import { api } from '@api/api';

export type ProgramCycleStatus = 'Active' | 'Draft' | 'Finished';

type ProgramCycleStatusQuery = 'ACTIVE' | 'DRAFT' | 'FINISHED';

export interface ProgramCyclesQuery {
  ordering: string;
  limit: number;
  offset: number;
  search?: string;
  title?: string;
  status?: ProgramCycleStatusQuery[];
  total_entitled_quantity_usd_from?: number;
  total_entitled_quantity_usd_to?: number;
  start_date?: string;
  end_date?: string;
}

export interface PaginatedListResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ProgramCycle {
  id: string;
  unicef_id: string;
  title: string;
  status: ProgramCycleStatus;
  start_date: string;
  end_date: string;
  program_start_date: string;
  program_end_date: string;
  created_at: string;
  created_by: string;
  total_entitled_quantity_usd: number;
  total_undelivered_quantity_usd: number;
  total_delivered_quantity_usd: number;
  frequency_of_payments: string;
  admin_url?: string;
  can_remove_cycle: boolean;
}

export const fetchProgramCycles = async (
  businessArea: string,
  programId: string,
  query: ProgramCyclesQuery,
): Promise<PaginatedListResponse<ProgramCycle>> => {
  const params = {
    offset: query.offset,
    limit: query.limit,
    ordering: query.ordering,
    title: query.title ?? '',
    search: query.search ?? '',
    total_entitled_quantity_usd_from:
      query.total_entitled_quantity_usd_from ?? '',
    total_entitled_quantity_usd_to: query.total_entitled_quantity_usd_to ?? '',
    start_date: query.start_date ?? '',
    end_date: query.end_date ?? '',
  } as ProgramCyclesQuery;
  if (query.status) {
    params.status = query.status;
  }
  return api.get(`${businessArea}/programs/${programId}/cycles/`, params);
};

export const fetchProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<ProgramCycle> => {
  return api.get(
    `${businessArea}/programs/${programId}/cycles/${programCycleId}/`,
  );
};

export interface ProgramCycleCreate {
  title: string;
  start_date: string;
  end_date?: string;
}

export interface ProgramCycleCreateResponse {
  data: ProgramCycleCreate;
}

export const createProgramCycle = async (
  businessArea: string,
  programId: string,
  body: ProgramCycleCreate,
): Promise<ProgramCycleCreateResponse> => {
  return api.post(`${businessArea}/programs/${programId}/cycles/`, body);
};

export interface ProgramCycleUpdate {
  title: string;
  start_date: string;
  end_date?: string;
}

export interface ProgramCycleUpdateResponse {
  data: ProgramCycleUpdate;
}

export const updateProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
  body: ProgramCycleUpdate,
): Promise<ProgramCycleUpdateResponse> => {
  return api.put(
    `${businessArea}/programs/${programId}/cycles/${programCycleId}/`,
    body,
  );
};
export const deleteProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<void> => {
  return api.delete(
    `${businessArea}/programs/${programId}/cycles/${programCycleId}/`,
  );
};

export const finishProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<any> => {
  return api.post(
    `${businessArea}/programs/${programId}/cycles/${programCycleId}/finish/`,
    {},
  );
};

export const reactivateProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<any> => {
  return api.post(
    `${businessArea}/programs/${programId}/cycles/${programCycleId}/reactivate/`,
    {},
  );
};
