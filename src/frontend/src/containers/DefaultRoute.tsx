import { useNavigate } from 'react-router-dom';
import { ReactElement, useEffect } from 'react';
import { useCachedMe } from '@hooks/useCachedMe';

export const DefaultRoute = (): ReactElement | null => {
  const { data } = useCachedMe();
  const navigate = useNavigate();

  useEffect(() => {
    if (data && data.me) {
      if (data.me.businessAreas.edges.length < 1) {
        navigate('/access-denied');
      } else {
        navigate(
          `/${data.me.businessAreas.edges[0].node.slug}/programs/all/list`,
        );
      }
    }
  }, [data, navigate]);

  return null;
};
