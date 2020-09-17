import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ProgramNode, useAllProgramsQuery } from '../../__generated__/graphql';
import { useDebounce } from '../../hooks/useDebounce';
import { PaymentVerificationTable } from '../tables/PaymentVerificationTable';
import { PaymentFilters } from '../tables/PaymentVerificationTable/PaymentFilters';
import { LoadingComponent } from '../../components/LoadingComponent';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PaymentVerificationPage(): React.ReactElement {
  const businessArea = useBusinessArea();

  const [filter, setFilter] = useState({
    search: '',
    program: '',
    assistanceThrough: '',
    deliveryType: '',
    startDate: null,
    endDate: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });
  if (loading) return <LoadingComponent />;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title='Payment Verification' />
      <PaymentFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
      />
      <Container data-cy='page-details-container'>
        <PaymentVerificationTable filter={debouncedFilter} />
      </Container>
    </div>
  );
}
