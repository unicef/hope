import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery, type UseQueryResult } from '@tanstack/react-query';

export const useHopeDetailsQuery = <TData, TOptions = any>(
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
