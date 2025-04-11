import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from './useBaseUrl';
import { Profile } from '@restgenerated/models/Profile';

export function usePermissions(): string[] {
  const { businessArea, programId } = useBaseUrl();
  const {
    data: meData,
    isLoading: meDataLoading,
    error,
  } = useQuery<Profile>({
    queryKey: ['profile', businessArea, programId],
    queryFn: () => {
      const params: { businessAreaSlug: string; programSlug?: string } = {
        businessAreaSlug: businessArea,
      };
      if (programId !== 'all') {
        params.programSlug = programId;
      }
      return RestService.restUsersProfileRetrieve(params);
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
