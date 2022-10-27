import get from 'lodash/get';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  ProgramNodeEdge,
  useAllProgramsQuery,
} from '../../../__generated__/graphql';
import { PaymentVerificationTable } from '../../tables/payments/PaymentVerificationTable';
import { PaymentFilters } from '../../tables/payments/PaymentVerificationTable/PaymentFilters';

export function PaymentVerificationPage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [filter, setFilter] = useState({
    search: '',
    verificationStatus: null,
    program: '',
    serviceProvider: '',
    deliveryType: null,
    startDate: null,
    endDate: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs: Array<ProgramNodeEdge["node"]> = allPrograms.map((edge: ProgramNodeEdge) => edge.node);

  return (
    <>
      <PageHeader title={t('Payment Verification')} />
      <PaymentFilters
        programs={programs}
        filter={filter}
        onFilterChange={setFilter}
      />
      <TableWrapper>
        <PaymentVerificationTable
          filter={debouncedFilter}
          businessArea={businessArea}
          canViewDetails={hasPermissions(
            PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
}
