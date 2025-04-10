import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from './useBaseUrl';
import { Profile } from '@restgenerated/models/Profile';

export function usePermissions(): string[] {
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const {
    data: meData,
    isLoading: meDataLoading,
    error,
  } = useQuery<Profile>({
    queryKey: ['profile', businessAreaSlug, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug,
        program: programSlug === 'all' ? undefined : programSlug,
      });
    },
  });

  if (meDataLoading) {
    return [];
  }

  if (error) {
    console.error('Error fetching permissions:', error);
    return [];
  }
  //@ts-ignore
  return meData?.permissionsInScope ?? [];
}
