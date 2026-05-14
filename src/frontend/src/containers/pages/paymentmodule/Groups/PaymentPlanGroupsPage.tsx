import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanGroupsFilters } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsFilters';
import { PaymentPlanGroupsTable } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsTable';
import { PageHeader } from '@core/PageHeader';
import { TableWrapper } from '@core/TableWrapper';
import { PermissionDenied } from '@core/PermissionDenied';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { getFilterFromQueryParams } from '@utils/utils';

const initialFilter = { search: '', cycle: '' };

const PaymentPlanGroupsPage = (): ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_PAYMENT_PLAN_GROUP, permissions))
    return (
      <PermissionDenied permission={PERMISSIONS.PM_VIEW_PAYMENT_PLAN_GROUP} />
    );

  return (
    <>
      <PageHeader title={t('Groups')} />
      <TableWrapper>
        <PaymentPlanGroupsFilters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={setAppliedFilter}
        />
      </TableWrapper>
      <TableWrapper>
        <PaymentPlanGroupsTable filter={appliedFilter} />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanGroupsPage,
  'PaymentPlanGroupsPage',
);
