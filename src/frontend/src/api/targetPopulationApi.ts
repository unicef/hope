import { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import { api, handleApiResponse } from './api';

export const fetchTargetPopulations = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<PaginatedPaymentPlanListList> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/targeting/target-populations/`,
      params,
    ),
  );
};
