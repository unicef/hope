import { useBaseUrl } from '@hooks/useBaseUrl';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

export function usePaymentPlan(
  paymentPlanId: string | null | undefined,
): UseQueryResult<PaymentPlanDetail> {
  const { businessArea, programId } = useBaseUrl();
  return useQuery<PaymentPlanDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
      {
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programCode: programId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programCode: programId,
      }),
    enabled: !!paymentPlanId && !!businessArea && !!programId,
  });
}
