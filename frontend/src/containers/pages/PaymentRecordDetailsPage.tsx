import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  PaymentRecordNode,
  usePaymentRecordQuery,
} from '../../__generated__/graphql';
import { PageHeader } from '../../components/PageHeader';
import { PaymentRecordDetails } from '../../components/payments/PaymentRecordDetails';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PaymentRecordDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data } = usePaymentRecordQuery({
    variables: { id },
  });
  if (!data) {
    return null;
  }
  const paymentRecord = data.paymentRecord as PaymentRecordNode;
  return (
    <div>
      <PageHeader title={`Payment ID ${paymentRecord.cashAssistId}`} />
      <Container>
        <PaymentRecordDetails paymentRecord={paymentRecord} />
      </Container>
    </div>
  );
}
