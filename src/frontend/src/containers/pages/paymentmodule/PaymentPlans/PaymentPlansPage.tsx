import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlansFilters } from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlansFilters';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlansTable';
import { PageHeader } from '@core/PageHeader';
import { TableWrapper } from '@core/TableWrapper';
import { PermissionDenied } from '@core/PermissionDenied';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { getFilterFromQueryParams } from '@utils/utils';

const initialFilter = { search: '', cycle: '', status: [] };

const PaymentPlansPage = (): ReactElement => {
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
  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_VIEW_LIST, permissions))
    return (
      <PermissionDenied permission={PERMISSIONS.PM_PAYMENT_PLAN_VIEW_LIST} />
    );

  return (
    <>
      <PageHeader title={t('Payment Plans')} />
      <TableWrapper>
        <PaymentPlansFilters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={setAppliedFilter}
        />
      </TableWrapper>
      <TableWrapper>
        <PaymentPlansTable filter={appliedFilter} />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(PaymentPlansPage, 'PaymentPlansPage');
