import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, UseQueryResult } from '@tanstack/react-query';

export function useVerificationStatusChoices(): UseQueryResult<Array<Choice>> {
  return useQuery<Array<Choice>>({
    queryKey: ['verificationStatusChoices'],
    queryFn: () => RestService.restChoicesPaymentVerificationStatusList(),
    staleTime: Infinity, // choices don't change within a session
  });
}
