import { useBaseUrl } from '@hooks/useBaseUrl';
import type { FspChoice } from '@restgenerated/models/FspChoice';
import type { FspChoices } from '@restgenerated/models/FspChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

export function useAvailableFspsForDeliveryMechanisms(): {
  data: FspChoices[] | undefined;
  isLoading: boolean;
} {
  const { businessArea } = useBaseUrl();
  return useQuery<FspChoices[]>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasAvailableFspsForDeliveryMechanismsList,
      { businessAreaSlug: businessArea },
    ),
    queryFn: () =>
      RestService.restBusinessAreasAvailableFspsForDeliveryMechanismsList({
        businessAreaSlug: businessArea,
      }),
  });
}

// The business area has no plain FSP list endpoint; the per-delivery-mechanism
// response lists every allowed FSP, so dedupe it.
export function useAvailableFsps(): FspChoice[] {
  const { data } = useAvailableFspsForDeliveryMechanisms();
  const byId = new Map<string, FspChoice>();
  (data ?? []).forEach((entry) =>
    entry.fsps.forEach((fsp) => byId.set(fsp.id, fsp)),
  );
  return [...byId.values()].sort((a, b) => a.name.localeCompare(b.name));
}
