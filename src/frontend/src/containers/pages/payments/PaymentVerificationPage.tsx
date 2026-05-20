import { ReactElement, useState, useRef } from 'react';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import PaymentVerificationFilters from '../../tables/payments/PaymentVerificationTable/PaymentVerificationFilters';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import withErrorBoundary from '@components/core/withErrorBoundary';
import PaymentVerificationTable from '@containers/tables/payments/PaymentVerificationTable/PaymentVerificationTable';

const initialFilter = {
  status: [PaymentPlanStatusEnum.FINISHED, PaymentPlanStatusEnum.ACCEPTED],
  search: '',
  paymentVerificationSummaryStatus: [],
  serviceProvider: '',
  deliveryTypes: [],
  startDate: '',
  endDate: '',
};

function PaymentVerificationPage(): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions))
    return (
      <PermissionDenied
        permission={PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST}
      />
    );

  return (
    <>
      <PageHeader title={t('Payment Verification')} />
      <PaymentVerificationFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <TableWrapper>
          <PaymentVerificationTable
            filter={appliedFilter}
            businessArea={businessArea}
            canViewDetails={hasPermissions(
              PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
              permissions,
            )}
          />
        </TableWrapper>
      </div>
    </>
  );
}
export default withErrorBoundary(
  PaymentVerificationPage,
  'PaymentVerificationPage',
);
