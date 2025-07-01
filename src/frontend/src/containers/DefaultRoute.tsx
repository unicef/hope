import { useNavigate } from 'react-router-dom';
import { ReactElement, useEffect } from 'react';
import { RestService } from '@restgenerated/index';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';

export const DefaultRoute = (): ReactElement | null => {
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const { data: meData } = useQuery({
    queryKey: ['profile', businessAreaSlug, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug,
        program: programSlug === 'all' ? undefined : programSlug,
      });
    },
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
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
