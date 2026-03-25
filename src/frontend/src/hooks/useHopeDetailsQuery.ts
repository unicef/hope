import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery, type UseQueryResult } from '@tanstack/react-query';

export const useHopeDetailsQuery = <TData, TOptions = any>(
  id: string,
  queryFn: (data: TOptions) => Promise<TData>,
  options: any,
): UseQueryResult<TData> => {
  const { businessAreaSlug, programCode } = useBaseUrl();
  return useQuery({
    queryKey: [queryFn.name, { id, programCode, businessAreaSlug }],
    queryFn: () =>
      queryFn({
        id,
        businessAreaSlug,
        programCode,
      } as TOptions),
    enabled: !!businessAreaSlug && !!programCode,
    ...options,
  }) as UseQueryResult<TData>;
};
