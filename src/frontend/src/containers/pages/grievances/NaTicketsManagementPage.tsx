import { NaTicketsManagement } from '@components/grievances/NeedsAdjudicationManagement/NaTicketsManagement';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import {
  GRIEVANCES_NA_MANAGE_PERMISSIONS,
  canManageNeedsAdjudication,
} from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

const NaTicketsManagementPage = (): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!canManageNeedsAdjudication(permissions))
    return <PermissionDenied permission={GRIEVANCES_NA_MANAGE_PERMISSIONS} />;

  return (
    <NaTicketsManagement
      onBack={() => navigate(`/${baseUrl}/grievance/tickets/user-generated`)}
    />
  );
};

export default withErrorBoundary(
  NaTicketsManagementPage,
  'NaTicketsManagementPage',
);
