import { useBaseUrl } from '@hooks/useBaseUrl';
import { QueryFunction, QueryKey, useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query/src/types';
import type { UndefinedInitialDataOptions } from '@tanstack/react-query/src/queryOptions';

export const useHopeDetailsQuery = <TData, TOptions>(
  id: string,
  queryFn: (data: TOptions) => Promise<TData>,
  options: any,
): UseQueryResult<TData> => {
  const { businessAreaSlug, programSlug } = useBaseUrl();
  return useQuery({
    queryKey: [queryFn.name, { id, programSlug, businessAreaSlug }],
    queryFn: () =>
      queryFn({
        id,
        businessAreaSlug,
        programSlug,
      } as TOptions),
    enabled: !!businessAreaSlug && !!programSlug,
    ...options,
  }) as UseQueryResult<TData>;
};
