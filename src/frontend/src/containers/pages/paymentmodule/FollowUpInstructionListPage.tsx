import withErrorBoundary from '@components/core/withErrorBoundary';
import { FollowUpInstructionTable } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionTable';
import { CreateFollowUpInstructionDialog } from '@containers/pages/paymentmodule/FollowUpInstructions/CreateFollowUpInstructionDialog';
import { PageHeader } from '@core/PageHeader';
import { TableWrapper } from '@core/TableWrapper';
import { PermissionDenied } from '@core/PermissionDenied';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

const FollowUpInstructionListPage = (): ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions))
    return <PermissionDenied permission={PERMISSIONS.PM_VIEW_LIST} />;

  return (
    <>
      <PageHeader title={t('Follow-up Instructions')}>
        <CreateFollowUpInstructionDialog />
      </PageHeader>
      <TableWrapper>
        <FollowUpInstructionTable />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(
  FollowUpInstructionListPage,
  'FollowUpInstructionListPage',
);
