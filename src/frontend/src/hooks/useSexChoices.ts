import { Choice } from '@restgenerated/models/Choice';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

export function useSexChoices(): Choice[] {
  const { businessArea } = useBaseUrl();
  const { data } = useQuery<IndividualChoices>({
    queryKey: ['individualChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasIndividualsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  return (data?.sexChoices ?? []) as Choice[];
}
