import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query/src/types';

export const useHopeDetailsQuery = (
  id: string,
  queryFn: (variables: any) => Promise<any>,
  refetchInterval: any = undefined,
): UseQueryResult => {
  const { businessArea, programSlug } = useBaseUrl();
  return useQuery({
    queryKey: [queryFn.name, id, programSlug, businessArea],
    queryFn: () =>
      queryFn({
        id,
        businessAreaSlug: businessArea,
        programSlug,
      }),
    refetchInterval,
    enabled: !!businessArea && !!programSlug,
  });
};
