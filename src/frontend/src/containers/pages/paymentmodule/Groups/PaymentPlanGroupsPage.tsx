import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanGroupsTable } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsTable';
import { PageHeader } from '@core/PageHeader';
import { TableWrapper } from '@core/TableWrapper';
import { PermissionDenied } from '@core/PermissionDenied';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

const PaymentPlanGroupsPage = (): ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_PAYMENT_PLAN_GROUP, permissions))
    return (
      <PermissionDenied permission={PERMISSIONS.PM_VIEW_PAYMENT_PLAN_GROUP} />
    );

  return (
    <>
      <PageHeader title={t('Groups')} />
      <TableWrapper>
        <PaymentPlanGroupsTable />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanGroupsPage,
  'PaymentPlanGroupsPage',
);
