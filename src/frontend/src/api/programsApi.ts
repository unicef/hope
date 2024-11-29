import { api } from './api';

interface BeneficiaryGroup {
  id: string;
  name: string;
  groupLabel: string;
  groupLabelPlural: string;
  memberLabel: string;
  memberLabelPlural: string;
  masterDetail: boolean;
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
