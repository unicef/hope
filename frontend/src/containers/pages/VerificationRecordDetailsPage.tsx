import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  PaymentRecordNode,
  usePaymentRecordQuery,
} from '../../__generated__/graphql';
import { PageHeader } from '../../components/PageHeader';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { VerificationRecordDetails } from '../../components/payments/VerificationRecordDetails';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;

export function VerificationRecordDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data, loading } = usePaymentRecordQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();

  // if (loading) {
  //   return <LoadingComponent />;
  // }

  // if (!data) {
  //   return null;
  // }

  // const paymentRecord = data.paymentRecord as PaymentRecordNode;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${businessArea}/payment-verification/`,
    },
    {
      title: 'Cash Plan ID here',
      to: `/${businessArea}/payment-verification/`,
    },
  ];

  const toolbar = (
    <PageHeader title='Payment ID id here' breadCrumbs={breadCrumbsItems} />
  );
  return (
    <div>
      {toolbar}
      <VerificationRecordDetails />
    </div>
  );
}
