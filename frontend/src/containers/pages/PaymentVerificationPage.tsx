import React, { useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ProgramNode, useAllProgramsQuery } from '../../__generated__/graphql';
import { useDebounce } from '../../hooks/useDebounce';
import { PaymentVerificationTable } from '../tables/PaymentVerificationTable';
import { PaymentFilters } from '../tables/PaymentVerificationTable/PaymentFilters';
import { LoadingComponent } from '../../components/LoadingComponent';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PaymentVerificationPage(): React.ReactElement {
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
  });
  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title='Payment Verification' />
      <PaymentFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
      />
      <Container data-cy='page-details-container'>
        <PaymentVerificationTable
          filter={debouncedFilter}
          businessArea={businessArea}
          canViewDetails={hasPermissions(
            PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
            permissions,
          )}
        />
      </Container>
    </div>
  );
}
