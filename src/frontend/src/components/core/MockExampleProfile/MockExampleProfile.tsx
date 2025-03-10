import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

const MockExampleProfile = () => {
  const { businessArea, programId } = useBaseUrl();

  const { data: meData, isLoading: meLoading } = useQuery({
    queryKey: ['profile', businessArea, programId],
    queryFn: () => {
      return RestService.restUsersProfileRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
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
          {meData?.first_name} {meData?.last_name}
        </div>
      )}
    </div>
  );
};

export default MockExampleProfile;
