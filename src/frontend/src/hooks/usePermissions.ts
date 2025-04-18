import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from './useBaseUrl';
import { Profile } from '@restgenerated/models/Profile';

export function usePermissions(): string[] {
  const { businessArea } = useBaseUrl();
  const {
    data: meData,
    isLoading: meDataLoading,
    error,
  } = useQuery<Profile>({
    queryKey: ['profile', businessArea],
    queryFn: () => {
      const params: { businessAreaSlug: string; program?: string } = {
        businessAreaSlug: businessArea,
      };
      return RestService.restBusinessAreasUsersProfileRetrieve(params);
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
