import get from 'lodash/get';
import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import {
  ProgramNodeEdge,
  useAllProgramsForChoicesQuery,
} from '../../../__generated__/graphql';
import { PaymentVerificationTable } from '../../tables/payments/PaymentVerificationTable';
import { PaymentFilters } from '../../tables/payments/PaymentVerificationTable/PaymentFilters';

const initialFilter = {
  search: '',
  verificationStatus: [],
  program: '',
  serviceProvider: '',
  deliveryType: '',
  startDate: undefined,
  endDate: undefined,
};

export const PaymentVerificationPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  if (loading) return <LoadingComponent />;
  if (!data || permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs: Array<ProgramNodeEdge['node']> = allPrograms.map(
    (edge: ProgramNodeEdge) => edge.node,
  );

  return (
    <>
      <PageHeader title={t('Payment Verification')} />
      <PaymentFilters
        programs={programs}
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
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
    </>
  );
};
