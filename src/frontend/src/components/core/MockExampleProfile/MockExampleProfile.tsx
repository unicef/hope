import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

const MockExampleProfile = () => {
  const { businessAreaSlug, programSlug } = useBaseUrl();

  const { data: meData, isLoading: meLoading } = useQuery({
    queryKey: ['profile', businessAreaSlug, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug: businessAreaSlug,
        program: programSlug,
      });
    },
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  return (
    <div style={{ border: '3px solid black', padding: '10px', width: '200px' }}>
      {meLoading ? (
        'Loading...'
      ) : (
        <div>
          <h4>Profile Details</h4>
          {meData?.firstName} {meData?.lastName}
        </div>
      )}
    </div>
  );
};

export default MockExampleProfile;
