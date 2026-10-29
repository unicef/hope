import { useBaseUrl } from '@hooks/useBaseUrl';
import type { PaymentPlanGroupDetail } from '@restgenerated/models/PaymentPlanGroupDetail';
import { RestService } from '@restgenerated/services/RestService';
import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

export function usePaymentPlanGroup(
  groupId: string | null | undefined,
): UseQueryResult<PaymentPlanGroupDetail> {
  const { businessArea, programId } = useBaseUrl();
  return useQuery<PaymentPlanGroupDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
      {
        businessAreaSlug: businessArea,
        id: groupId,
        programCode: programId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve({
        businessAreaSlug: businessArea,
        id: groupId,
        programCode: programId,
      }),
    enabled: !!groupId && !!businessArea && !!programId,
  });
}
