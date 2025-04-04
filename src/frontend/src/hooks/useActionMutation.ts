import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  QueryFunction,
  QueryKey,
  useMutation,
  UseMutationResult,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query/src/types';
import type { UndefinedInitialDataOptions } from '@tanstack/react-query/src/queryOptions';
import { RestService } from '@restgenerated/services/RestService';
import type { DefaultError } from '@tanstack/query-core';

export const useHopeDetailsQuery = <TData, TOptions>(
  id: string,
  mutationFn: (data: TOptions) => Promise<TData>,
  invalidateQuery: string[],
  options: any = null,
): UseMutationResult<TData, DefaultError, void> => {
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const client = useQueryClient();
  return useMutation({
    mutationFn: async () =>
      mutationFn({
        businessAreaSlug,
        programSlug,
        id: id,
      } as TOptions),
    ...options,
    onSuccess: async () => {
      if (options?.onSuccess) {
        await options.onSuccess();
      }
      if (invalidateQuery) {
        await client.invalidateQueries({
          queryKey: invalidateQuery,
        });
      }
    },
  }) as UseMutationResult<TData, DefaultError, void>;
};
