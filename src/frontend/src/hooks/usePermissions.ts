import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from './useBaseUrl';
import { Profile } from '@restgenerated/models/Profile';
import { restQueryKey } from '@utils/queryKeys';
import { useMemo } from 'react';

export function usePermissions(): string[] {
  const { businessAreaSlug, programCode } = useBaseUrl();

  const profileParams = {
    businessAreaSlug,
    program: programCode === 'all' ? undefined : programCode,
  };

  const {
    data: meData,
    isLoading: meDataLoading,
    error,
  } = useQuery<Profile>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersProfileRetrieve,
      profileParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve(profileParams);
    },
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  return useMemo(() => {
    if (meDataLoading) {
      // Return null while loading to indicate permissions aren't ready yet
      return null;
    }

    if (error) {
      console.error('Error fetching permissions:', error);
      return [];
    }

    // Make sure we always return a string array
    const permissionsData = meData?.permissionsInScope;
    if (!permissionsData) {
      return [];
    }

    // Handle both string and array types
    return Array.isArray(permissionsData) ? permissionsData : [permissionsData];
  }, [meData, meDataLoading, error]);
}
