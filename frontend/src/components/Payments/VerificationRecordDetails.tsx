import { Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import {
  formatCurrencyWithSymbol,
  paymentRecordStatusToColor,
  verificationRecordsStatusToColor,
} from '../../utils/utils';
import { PaymentVerificationNode } from '../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { LabelizedField } from '../LabelizedField';
import { StatusBox } from '../StatusBox';
import { UniversalMoment } from '../UniversalMoment';

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
  paymentVerification: PaymentVerificationNode;
  canViewActivityLog: boolean;
}

export function VerificationRecordDetails({
  paymentVerification,
  canViewActivityLog,
}: VerificationRecordDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Payment Record Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
              <StatusContainer>
                <StatusBox
                  status={paymentVerification.paymentRecord.status}
                  statusToColor={paymentRecordStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('REGISTRATION GROUP')}
              value={paymentVerification.paymentRecord.registrationCaId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TARGET POPULATION')}
              value={paymentVerification.paymentRecord.targetPopulation.name}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DISTRIBUTION MODALITY')}
              value={paymentVerification.paymentRecord.distributionModality}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Verification Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
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
              label={t('AMOUNT RECEIVED')}
              value={formatCurrencyWithSymbol(
                paymentVerification.receivedAmount,
                paymentVerification.paymentRecord.currency,
              )}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Household')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('HOUSEHOLD ID')}
              value={paymentVerification.paymentRecord.household.unicefId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('HEAD OF HOUSEHOLD')}
              value={paymentVerification.paymentRecord.fullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TOTAL PERSON COVERED')}
              value={paymentVerification.paymentRecord.totalPersonsCovered}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('PHONE NUMBER')}
              value={
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNo
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ALT. PHONE NUMBER')}
              value={
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNoAlternative
              }
            />
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Entitlement Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT QUANTITY')}
              value={paymentVerification.paymentRecord.entitlementQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={paymentVerification.paymentRecord.deliveredQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('CURRENCY')}
              value={paymentVerification.paymentRecord.currency}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY TYPE')}
              value={paymentVerification.paymentRecord.deliveryType}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={
                <UniversalMoment>
                  {paymentVerification.paymentRecord.deliveryDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT CARD ID')}
              value={paymentVerification.paymentRecord.entitlementCardNumber}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TRANSACTION REFERENCE ID')}
              value={paymentVerification.paymentRecord.transactionReferenceId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT CARD ISSUE DATE')}
              value={
                <UniversalMoment>
                  {paymentVerification.paymentRecord.entitlementCardIssueDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('FSP')}
              value={paymentVerification.paymentRecord.serviceProvider.fullName}
            />
          </Grid>
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <TableWrapper>
          <UniversalActivityLogTable objectId={paymentVerification.id} />
        </TableWrapper>
      )}
    </>
  );
}
