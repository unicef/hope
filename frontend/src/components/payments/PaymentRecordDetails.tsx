import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import {
  formatCurrency,
  paymentRecordStatusToColor,
  verificationRecordsStatusToColor,
} from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import {
  PaymentRecordNode,
  PaymentVerificationNode,
} from '../../__generated__/graphql';
import { Missing } from '../Missing';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import { UniversalMoment } from '../UniversalMoment';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface VerificationRecordDetailsProps {
  paymentRecord: PaymentRecordNode;
}

export function PaymentRecordDetails({
  paymentRecord,
}: VerificationRecordDetailsProps): React.ReactElement {
  let paymentVerification: PaymentVerificationNode = null;
  if (paymentRecord.verifications.totalCount > 0) {
    paymentVerification = paymentRecord.verifications.edges[0].node;
  }
  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>Payment Record Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='STATUS'>
              <StatusContainer>
                <StatusBox
                  status={paymentRecord.status}
                  statusToColor={paymentRecordStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='STATUS DATE'
              value={
                <UniversalMoment>{paymentRecord.statusDate}</UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='REGISTRATION GROUP'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='TARGET POPULATION'
              value={paymentRecord.targetPopulation.name}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DISTRIBUTION MODALITY'
              value={paymentRecord.distributionModality}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      {paymentVerification != null ? (
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant='h6'>Verification Details</Typography>
          </Title>
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <LabelizedField label='STATUS'>
                <StatusContainer>
                  <StatusBox
                    status={paymentVerification.status}
                    statusToColor={verificationRecordsStatusToColor}
                  />
                </StatusContainer>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField
                label='STATUS DATE'
                value={
                  <UniversalMoment>
                    {paymentVerification.statusDate}
                  </UniversalMoment>
                }
              />
            </Grid>
            <Grid item xs={3}>
              <LabelizedField
                label='AMOUNT RECEIVED'
                value={formatCurrency(paymentVerification.receivedAmount)}
              />
            </Grid>
          </Grid>
        </ContainerColumnWithBorder>
      ) : null}
      <Overview>
        <Title>
          <Typography variant='h6'>Household</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label='HOUSEHOLD ID'
              value={paymentRecord.household.unicefId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='HEAD OF HOUSEHOLD'
              value={paymentRecord.fullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='TOTAL PERSON COVERED'
              value={paymentRecord.totalPersonsCovered}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='PHONE NUMBER'
              value={paymentRecord.household.headOfHousehold.phoneNo}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='ALT. PHONE NUMBER'
              value={
                paymentRecord.household.headOfHousehold.phoneNoAlternative ||
                '-'
              }
            />
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>Entitlement Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label='ENTITLEMENT QUANTITY'
              value={paymentRecord.entitlementQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DELIVERED QUANTITY'
              value={paymentRecord.deliveredQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='CURRENCY' value={paymentRecord.currency} />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DELIVERY TYPE'
              value={paymentRecord.deliveryType}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DELIVERY DATE'
              value={
                <UniversalMoment>{paymentRecord.deliveryDate}</UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='ENTITLEMENT CARD ID'
              value={paymentRecord.entitlementCardNumber}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='TRANSACTION REFERENCE ID'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='ENTITLEMENT CARD ISSUE DATE'
              value={
                <UniversalMoment>
                  {paymentRecord.entitlementCardIssueDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='FSP'
              value={paymentRecord.serviceProvider.fullName}
            />
          </Grid>
        </Grid>
      </Overview>
      {paymentVerification != null ? (
        <TableWrapper>
          <UniversalActivityLogTable objectId={paymentVerification.id} />
        </TableWrapper>
      ) : null}
    </>
  );
}
