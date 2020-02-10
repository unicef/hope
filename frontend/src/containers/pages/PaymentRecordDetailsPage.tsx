import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  PaymentRecordNode,
  usePaymentRecordQuery,
} from '../../__generated__/graphql';
import { PageHeader } from '../../components/PageHeader';
import { PaymentRecordDetails } from '../../components/payments/PaymentRecordDetails';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PaymentRecordDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data, error } = usePaymentRecordQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();
  console.log('data', data, error);
  if (!data) {
    return null;
  }
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Managment',
      to: `/${businessArea}/programs/`,
    },
    {
      title: data.paymentRecord.cashPlan.program.name,
      to: `/${businessArea}/programs/${data.paymentRecord.cashPlan.program.id}/`,
    },
    {
      title: `Cash Plan #${data.paymentRecord.cashPlan.cashAssistId}`,
      to: `/${businessArea}/cashplans/${data.paymentRecord.cashPlan.id}`,
    },
  ];
  const paymentRecord = data.paymentRecord as PaymentRecordNode;
  return (
    <div>
      <PageHeader
        title={`Payment ID ${paymentRecord.cashAssistId}`}
        breadCrumbs={breadCrumbsItems}
      />
      <Container>
        <PaymentRecordDetails paymentRecord={paymentRecord} />
      </Container>
    </div>
  );
}
