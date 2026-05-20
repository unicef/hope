import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  useMutation,
  UseMutationResult,
  useQueryClient,
} from '@tanstack/react-query';
import type { DefaultError } from '@tanstack/query-core';

export const useActionMutation = <TData, TOptions>(
  id: string,
  mutationFn: (data: TOptions) => Promise<TData>,
  invalidateQuery: string[],
  options: any = null,
): UseMutationResult<TData, DefaultError, void> => {
  const { businessAreaSlug, programCode } = useBaseUrl();
  const client = useQueryClient();
  return useMutation({
    mutationFn: async() =>
      mutationFn({
        businessAreaSlug,
        programCode,
        id: id,
      } as TOptions),
    ...options,
    onSuccess: async() => {
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
