import React from 'react';
import {useParams} from 'react-router-dom';
import styled from 'styled-components';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import {Button} from '@material-ui/core';
import {PaymentRecordNode, useCashAssistUrlPrefixQuery, usePaymentRecordQuery,} from '../../__generated__/graphql';
import {PageHeader} from '../../components/PageHeader';
import {PaymentRecordDetails} from '../../components/payments/PaymentRecordDetails';
import {BreadCrumbsItem} from '../../components/BreadCrumbs';
import {useBusinessArea} from '../../hooks/useBusinessArea';
import {LoadingComponent} from '../../components/LoadingComponent';
import {usePermissions} from '../../hooks/usePermissions';
import {hasPermissions, PERMISSIONS} from '../../config/permissions';
import {PermissionDenied} from '../../components/PermissionDenied';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;
const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export function PaymentRecordDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery();
  const { data, loading } = usePaymentRecordQuery({
    variables: { id },
  });
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  if (loading || caLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
      permissions,
    )
  )
    return <PermissionDenied />;

  if (!data || !caData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Management',
      to: `/${businessArea}/programs/`,
    },
    {
      title: data.paymentRecord.cashPlan.program.name,
      to: `/${businessArea}/programs/${data.paymentRecord.cashPlan.program.id}/`,
    },
    {
      title: `Cash Plan #${data.paymentRecord.cashPlan.caId}`,
      to: `/${businessArea}/cashplans/${data.paymentRecord.cashPlan.id}`,
    },
  ];
  const paymentRecord = data.paymentRecord as PaymentRecordNode;
  return (
    <div>
      <PageHeader
        title={`Payment ID ${paymentRecord.caId}`}
        breadCrumbs={breadCrumbsItems}
      >
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            component='a'
            disabled={!paymentRecord.caHashId || !caData?.cashAssistUrlPrefix}
            target='_blank'
            href={`${caData?.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_payment&id=${paymentRecord.caHashId}`}
            startIcon={<OpenInNewRoundedIcon />}
          >
            Open in CashAssist
          </Button>
        </ButtonContainer>
      </PageHeader>
      <Container>
        <PaymentRecordDetails
          paymentRecord={paymentRecord}
          canViewActivityLog={hasPermissions(
            PERMISSIONS.ACTIVITY_LOG_VIEW,
            permissions,
          )}
        />
      </Container>
    </div>
  );
}
