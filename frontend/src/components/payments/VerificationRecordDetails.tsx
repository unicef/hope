import { Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  getPhoneNoLabel,
  paymentRecordStatusToColor,
  verificationRecordsStatusToColor,
} from '../../utils/utils';
import { PaymentVerificationNode } from '../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../core/ContainerColumnWithBorder';
import { LabelizedField } from '../core/LabelizedField';
import { StatusBox } from '../core/StatusBox';
import { UniversalMoment } from '../core/UniversalMoment';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BlackLink } from '../core/BlackLink';
import { Title } from '../core/Title';

const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

interface VerificationRecordDetailsProps {
  paymentVerification: PaymentVerificationNode;
  canViewActivityLog: boolean;
  choicesData;
}

export function VerificationRecordDetails({
  paymentVerification,
  canViewActivityLog,
  choicesData,
}: VerificationRecordDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const deliveryTypeDict = choicesToDict(
    choicesData.paymentRecordDeliveryTypeChoices,
  );

  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Payment Record Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={paymentVerification.paymentRecord.status}
                statusToColor={paymentRecordStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('REGISTRATION GROUP')}>
              <BlackLink
                to={`/${businessArea}/population/household/${paymentVerification.paymentRecord.household.id}`}
              >
                {paymentVerification.paymentRecord.household.unicefId}
              </BlackLink>
            </LabelizedField>
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
              <StatusBox
                status={paymentVerification.status}
                statusToColor={verificationRecordsStatusToColor}
              />
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
              value={getPhoneNoLabel(
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNo,
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNoValid,
              )}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ALT. PHONE NUMBER')}
              value={getPhoneNoLabel(
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNoAlternative,
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNoAlternativeValid,
              )}
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
              value={
                deliveryTypeDict[paymentVerification.paymentRecord.deliveryType]
              }
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
        <UniversalActivityLogTable objectId={paymentVerification.id} />
      )}
    </>
  );
}
