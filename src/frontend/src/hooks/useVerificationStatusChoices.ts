import type { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

export function useVerificationStatusChoices(): UseQueryResult<Array<Choice>> {
  return useQuery<Array<Choice>>({
    queryKey: restQueryKey(
      RestService.restChoicesPaymentVerificationStatusList,
    ),
    queryFn: () => RestService.restChoicesPaymentVerificationStatusList(),
    staleTime: Infinity, // choices don't change within a session
  });
}
