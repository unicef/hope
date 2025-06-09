import { api, handleMutationError } from 'src/api/api';

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
  try {
    const response = await api.post(
      `${businessArea}/programs/${programId}/cycles/`,
      body,
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'create program cycle');
  }
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
  try {
    const response = await api.put(
      `${businessArea}/programs/${programId}/cycles/${programCycleId}/`,
      body,
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'update program cycle');
  }
};

export const deleteProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<void> => {
  try {
    await api.delete(
      `${businessArea}/programs/${programId}/cycles/${programCycleId}/`,
    );
  } catch (error) {
    handleMutationError(error, 'delete program cycle');
  }
};

export const finishProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<any> => {
  try {
    const response = await api.post(
      `${businessArea}/programs/${programId}/cycles/${programCycleId}/finish/`,
      {},
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'finish program cycle');
  }
};

export const reactivateProgramCycle = async (
  businessArea: string,
  programId: string,
  programCycleId: string,
): Promise<any> => {
  try {
    const response = await api.post(
      `${businessArea}/programs/${programId}/cycles/${programCycleId}/reactivate/`,
      {},
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'reactivate program cycle');
  }
};
