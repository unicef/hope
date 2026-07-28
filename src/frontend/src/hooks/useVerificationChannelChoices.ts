import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export function useVerificationChannelChoices(): Choice[] {
  const { data } = useQuery<Array<Choice>>({
    queryKey: ['verificationChannelChoices'],
    queryFn: () => RestService.restChoicesPaymentVerificationPlanChannelList(),
    staleTime: Infinity, // choices don't change within a session
  });

  return (data ?? []).map((choice) => ({
    ...choice,
    dataCy: `radio-${choice.value.toLowerCase()}`,
  }));
}
