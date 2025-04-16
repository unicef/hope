import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Profile } from '@restgenerated/models/Profile';

const MockExampleProfile = () => {
  const { businessArea } = useBaseUrl();

  const { data: meData, isLoading: meLoading } = useQuery<Profile>({
    queryKey: ['profile', businessArea],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug: businessArea,
      });
    },
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
