import { useBaseUrl } from '@hooks/useBaseUrl';
import { QueryFunction, QueryKey, useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query/src/types';
import type { UndefinedInitialDataOptions } from '@tanstack/react-query/src/queryOptions';

export const useHopeDetailsQuery = <TData,TOptions>(
  id: string,
  queryFn: (data:TOptions)=>Promise<TData>,
  options: any
): UseQueryResult<TData> => {
  const { businessArea, programSlug } = useBaseUrl();
  return useQuery({
    queryKey: [queryFn.name, id, programSlug, businessArea],
    queryFn: () =>
      queryFn({
        id,
        businessAreaSlug: businessArea,
        programSlug,
      } as TOptions),
    enabled: !!businessArea && !!programSlug,
    ...options
  }) as UseQueryResult<TData>;
};
