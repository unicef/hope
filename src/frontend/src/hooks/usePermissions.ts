import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from './useBaseUrl';

export function usePermissions(): string[] {
  const { businessArea, programId } = useBaseUrl();
  const { data: meData, isLoading: meDataLoading } = useQuery({
    queryKey: ['profile', businessArea, programId],
    queryFn: () => {
      return RestService.restUsersProfileRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      });
    },
  });

  if (!meData || !meDataLoading) {
    return [];
  }
  console.log(meData);
  return (
    (meData as { permissions_in_scope?: string[] })?.permissions_in_scope ?? []
  );
}
