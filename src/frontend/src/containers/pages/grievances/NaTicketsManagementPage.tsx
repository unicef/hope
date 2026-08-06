import { NaTicketsManagement } from '@components/grievances/NeedsAdjudicationManagement/NaTicketsManagement';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

const naManagePermissions = [
  PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
  PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
  PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
];

const NaTicketsManagementPage = (): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(naManagePermissions, permissions))
    return <PermissionDenied permission={naManagePermissions} />;

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
