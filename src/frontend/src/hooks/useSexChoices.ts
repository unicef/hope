import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';

export function useSexChoices(): UseQueryResult<Array<Choice>> {
  return useQuery<Array<Choice>>({
    queryKey: restQueryKey(RestService.restChoicesSexList),
    queryFn: () => RestService.restChoicesSexList(),
    staleTime: Infinity, // choices don't change within a session
  });
}
