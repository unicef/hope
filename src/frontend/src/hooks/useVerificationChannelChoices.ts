import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { fieldNameToLabel } from '@utils/utils';

export function useVerificationChannelChoices(): UseQueryResult<Array<Choice>> {
  return useQuery<Array<Choice>>({
    queryKey: restQueryKey(
      RestService.restChoicesPaymentVerificationPlanChannelList,
    ),
    queryFn: () => RestService.restChoicesPaymentVerificationPlanChannelList(),
    staleTime: Infinity, // choices don't change within a session
    // Selenium selects the radios by data-cy (radio-manual / radio-rapidpro / radio-xlsx).
    select: (choices) =>
      choices.map((choice) => ({
        ...choice,
        name: fieldNameToLabel(choice.name),
        dataCy: `radio-${choice.value.toLowerCase()}`,
      })),
  });
}
