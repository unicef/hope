import { useBaseUrl } from '@hooks/useBaseUrl';
import type { UseMutationResult } from '@tanstack/react-query';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { DefaultError, QueryKey } from '@tanstack/query-core';

export const useActionMutation = <TData, TOptions>(
  id: string,
  mutationFn: (data: TOptions) => Promise<TData>,
  // Derive via restQueryKey (utils/queryKeys.ts) so this matches the reader's key.
  invalidateQuery: QueryKey,
  options: any = null,
): UseMutationResult<TData, DefaultError, void> => {
  const { businessAreaSlug, programCode } = useBaseUrl();
  const client = useQueryClient();
  return useMutation({
    mutationFn: async () =>
      mutationFn({
        businessAreaSlug,
        programCode,
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
  });
};
