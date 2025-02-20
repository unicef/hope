import { api, handleApiResponse } from './api';

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
