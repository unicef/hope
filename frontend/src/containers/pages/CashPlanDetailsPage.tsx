import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { PageHeader } from '../../components/PageHeader';
import { CashPlanDetails } from '../../components/CashPlanDetails';
import { useCashPlanQuery, CashPlanNode } from '../../__generated__/graphql';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function CashPlanDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data } = useCashPlanQuery({
    variables: { id },
  });

  if (!data) {
    return null;
  }
  const cashPlan = data.cashPlan as CashPlanNode
  //eslint-disable-next-line
  console.log(cashPlan)
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
        <CashPlanDetails cashPlan={cashPlan}/>
      </Container>
    </div>
  );
}
