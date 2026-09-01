import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

export const useHopeDetailsQuery = <TData, TOptions = any>(
  id: string,
  queryFn: (data: TOptions) => Promise<TData>,
  options: any,
): UseQueryResult<TData> => {
  const { businessAreaSlug, programCode } = useBaseUrl();
  return useQuery({
    queryKey: restQueryKey(queryFn, { id, programCode, businessAreaSlug }),
    queryFn: () =>
      queryFn({
        id,
        businessAreaSlug,
        programCode,
      } as TOptions),
    enabled: !!businessAreaSlug && !!programCode,
    ...options,
  });
};
