import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  ProgramNode,
  useAllProgramsQuery,
  useAllCashPlansQuery,
  useProgramQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
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
  const { id } = useParams();
  const { data, loading } = useProgramQuery({
    variables: { id },
  });
  const {
    data: choices,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  // if (loading || choicesLoading) {
  //   return <LoadingComponent />;
  // }
  // if (!data || !choices) {
  //   return null;
  // }
  // const program = data.program as ProgramNode;

  return (
    <div>
      <PageHeader title='Payment Verification' />
      {/* <PaymentFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      /> */}
      <Container data-cy='page-details-container'>
        <PaymentVerificationTable program={null} />
      </Container>
    </div>
  );
}
