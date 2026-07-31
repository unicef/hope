import { ReactElement, useEffect } from 'react';
import { RestService } from '@restgenerated/index';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { restQueryKey } from '@utils/queryKeys';

export const DefaultRoute = (): ReactElement | null => {
  const { businessAreaSlug, programCode } = useBaseUrl();

  const profileParams = {
    businessAreaSlug,
    program: programCode === 'all' ? undefined : programCode,
  };

  const { data: meData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersProfileRetrieve,
      profileParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve(profileParams);
    },
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus,
    retry: false,
  });
  const navigate = useNavigate();

  useEffect(() => {
    if (meData) {
      if (meData.businessAreas.length < 1) {
        navigate('/access-denied');
      } else {
        navigate(`/${meData.businessAreas[0].slug}/programs/all/list`);
      }
    }
  }, [meData, navigate]);

  return null;
};
