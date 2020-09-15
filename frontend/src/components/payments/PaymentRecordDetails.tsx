import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import { Grid, Paper, Typography } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import {
  decodeIdString,
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

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

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
      <Container>
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
              value={moment(paymentRecord.statusDate).format('DD MMM YYYY')}
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
      </Container>
      {paymentVerification != null ? (
        <Container>
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
                value={moment(paymentVerification.statusDate).format(
                  'DD MMM YYYY',
                )}
              />
            </Grid>
            <Grid item xs={3}>
              <LabelizedField
                label='AMOUNT RECEIVED'
                value={formatCurrency(paymentVerification.receivedAmount)}
              />
            </Grid>
          </Grid>
        </Container>
      ) : null}
      <Overview>
        <Title>
          <Typography variant='h6'>Household</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label='HOUSEHOLD ID'
              value={decodeIdString(paymentRecord.household.id)}
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
              value={paymentRecord.household.headOfHousehold.phoneNoAlternative}
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
              value={moment(paymentRecord.deliveryDate).format('DD MMM YYYY')}
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
              value={moment(paymentRecord.entitlementCardIssueDate).format(
                'DD MMM YYYY',
              )}
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
