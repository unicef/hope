import { NaTicketsManagement } from '@components/grievances/NeedsAdjudicationManagement/NaTicketsManagement';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

const NaTicketsManagementPage = (): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();

  return (
    <NaTicketsManagement
      onBack={() => navigate(`/${baseUrl}/grievance/tickets/system-generated`)}
    />
  );
};

export default withErrorBoundary(
  NaTicketsManagementPage,
  'NaTicketsManagementPage',
);
