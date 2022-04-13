import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { PaymentPlansTable } from '../../tables/paymentmodule/PaymentPlansTable';
import { PaymentPlansFilters } from '../../tables/paymentmodule/PaymentPlansTable/PaymentPlansFilters';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const TableWrapper = styled.div`
  padding: 20px;
`;

export function PaymentModulePage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [filter, setFilter] = useState({
    search: '',
    dispersionDate: '',
    status: '',
    entitlement: { min: null, max: null },
  });
  const debouncedFilter = useDebounce(filter, 500);

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <div>
      <PageHeader title={t('Payment Module')} />
      <PaymentPlansFilters filter={filter} onFilterChange={setFilter} />
      <Container data-cy='page-details-container'>
        <TableWrapper>
          <PaymentPlansTable
            filter={debouncedFilter}
            businessArea={businessArea}
            canViewDetails={hasPermissions(
              PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
              permissions,
            )}
          />
        </TableWrapper>
      </Container>
    </div>
  );
}
