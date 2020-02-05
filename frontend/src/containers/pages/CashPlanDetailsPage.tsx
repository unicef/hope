import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { PageHeader } from '../../components/PageHeader';
import { CashPlanDetails } from '../../components/CashPlanDetails';
import { PaymentRecordTable } from '../PaymentRecordTable';
import { useCashPlanQuery, CashPlanNode } from '../../__generated__/graphql';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
`;

export function CashPlanDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data } = useCashPlanQuery({
    variables: { id },
  });

  if (!data) {
    return null;
  }
  const cashPlan = data.cashPlan as CashPlanNode;
  return (
    <div>
      <PageHeader
        title={`Cash Plan #${data.cashPlan.cashAssistId}`}
        category='Programme Management'
      >
        <Button variant='contained' color='primary'>
          open in cashassist
        </Button>
      </PageHeader>
      <Container>
        <CashPlanDetails cashPlan={cashPlan} />
        <TableWrapper>
          <PaymentRecordTable cashPlan={cashPlan} />
        </TableWrapper>
      </Container>
    </div>
  );
}
