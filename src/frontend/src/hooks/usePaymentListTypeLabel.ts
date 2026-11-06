import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

/**
 * Resolves a PaymentList `planType` value to its human-readable label via the
 * `/api/rest/choices/payment-list-type/` endpoint — the single source of truth
 * for choice labels. `PlanTypeEnum` is kept only for static branching in code.
 */
export function usePaymentListTypeLabel(): (
  planType?: string | null,
) => string {
  const { data } = useQuery({
    queryKey: restQueryKey(RestService.restChoicesPaymentListTypeList),
    queryFn: () => RestService.restChoicesPaymentListTypeList(),
  });

  return (planType): string =>
    data?.find((choice) => choice.value === planType)?.name ?? '';
}
