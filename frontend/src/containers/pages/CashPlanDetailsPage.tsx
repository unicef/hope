import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { PageHeader } from '../../components/PageHeader';
import { CashPlanDetails } from '../../components/CashPlanDetails';
import { PaymentRecordTable } from '../tables/PaymentRecordTable';
import { useCashPlanQuery, CashPlanNode } from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';

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
  const { data, loading } = useCashPlanQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();

  if (loading) {
    return <LoadingComponent />;
  }
  if (!data) {
    return null;
  }
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Managment',
      to: `/${businessArea}/programs/`,
    },
    {
      title: data.cashPlan.program.name,
      to: `/${businessArea}/programs/${data.cashPlan.program.id}/`,
    },
  ];
  const cashPlan = data.cashPlan as CashPlanNode;
  return (
    <div>
      <PageHeader
        title={`Cash Plan #${data.cashPlan.cashAssistId}`}
        breadCrumbs={breadCrumbsItems}
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
