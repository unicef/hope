import { api } from './api';

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
  return api.get('beneficiary-groups/');
};
