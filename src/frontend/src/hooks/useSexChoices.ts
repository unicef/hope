import { Choice } from '@restgenerated/models/Choice';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export function useSexChoices(): Choice[] {
  const { data } = useQuery<Array<Choice>>({
    queryKey: ['sexChoices'],
    queryFn: () => RestService.restChoicesSexList(),
    staleTime: Infinity, // choices don't change within a session
  });

  return data ?? [];
}
