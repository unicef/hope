import { Choice } from '@restgenerated/models/Choice';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

/**
 * Returns the sex/gender choices from the `individuals/choices/` endpoint — the
 * single source of truth for these labels — instead of hardcoding the option
 * list in each form. The query is deduped by react-query across all consumers.
 */
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
