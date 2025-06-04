import { ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { PeoplePaymentPlansTable } from '@containers/tables/paymentmodulePeople/PeoplePaymentPlansTable';
import { PeoplePaymentPlansFilters } from '@containers/tables/paymentmodulePeople/PeoplePaymentPlansTable/PeoplePaymentPlansFilters';
import withErrorBoundary from '@components/core/withErrorBoundary';

const initialFilter = {
  search: '',
  dispersionStartDate: '',
  dispersionEndDate: '',
  status: [],
  totalEntitledQuantityFrom: '',
  totalEntitledQuantityTo: '',
  isFollowUp: '',
};

export const PeoplePaymentModulePage = (): ReactElement => {
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

  if (!hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Payment Module')} />
      <PeoplePaymentPlansFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <PeoplePaymentPlansTable
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.PM_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
};
export default withErrorBoundary(
  PeoplePaymentModulePage,
  'PeoplePaymentModulePage',
);
