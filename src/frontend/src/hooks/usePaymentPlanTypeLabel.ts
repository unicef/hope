import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

/**
 * Resolves a PaymentPlan `planType` value to its human-readable label via the
 * `/api/rest/choices/payment-plan-type/` endpoint — the single source of truth
 * for choice labels. `PlanTypeEnum` is kept only for static branching in code.
 */
export function usePaymentPlanTypeLabel(): (
  planType?: string | null,
) => string {
  const { data } = useQuery({
    queryKey: ['paymentPlanTypeChoices'],
    queryFn: () => RestService.restChoicesPaymentPlanTypeList(),
  });

  return (planType): string =>
    data?.find((choice) => choice.value === planType)?.name ?? '';
}
