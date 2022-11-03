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
import { PaymentRecordNode } from '../../__generated__/graphql';
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
  paymentRecord: PaymentRecordNode;
  canViewActivityLog: boolean;
  choicesData;
}

export function VerificationRecordDetails({
  paymentRecord,
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
                status={paymentRecord.status}
                statusToColor={paymentRecordStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('REGISTRATION GROUP')}>
              <BlackLink
                to={`/${businessArea}/population/household/${paymentRecord.household.id}`}
              >
                {paymentRecord.household.unicefId}
              </BlackLink>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TARGET POPULATION')}
              value={paymentRecord.targetPopulation.name}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DISTRIBUTION MODALITY')}
              value={paymentRecord.distributionModality}
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
                status={paymentRecord.verification.status}
                statusToColor={verificationRecordsStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('AMOUNT RECEIVED')}
              value={formatCurrencyWithSymbol(
                paymentRecord.verification.receivedAmount,
                paymentRecord.currency,
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
              value={paymentRecord.household.unicefId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('HEAD OF HOUSEHOLD')}
              value={paymentRecord.fullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TOTAL PERSON COVERED')}
              value={paymentRecord.totalPersonsCovered}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('PHONE NUMBER')}
              value={getPhoneNoLabel(
                paymentRecord.household.headOfHousehold
                  .phoneNo,
                paymentRecord.household.headOfHousehold
                  .phoneNoValid,
              )}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ALT. PHONE NUMBER')}
              value={getPhoneNoLabel(
                paymentRecord.household.headOfHousehold
                  .phoneNoAlternative,
                paymentRecord.household.headOfHousehold
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
              value={paymentRecord.entitlementQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={paymentRecord.deliveredQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('CURRENCY')}
              value={paymentRecord.currency}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY TYPE')}
              value={
                deliveryTypeDict[paymentRecord.deliveryType]
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={
                <UniversalMoment>
                  {paymentRecord.deliveryDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT CARD ID')}
              value={paymentRecord.entitlementCardNumber}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TRANSACTION REFERENCE ID')}
              value={paymentRecord.transactionReferenceId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT CARD ISSUE DATE')}
              value={
                <UniversalMoment>
                  {paymentRecord.entitlementCardIssueDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('FSP')}
              value={paymentRecord.serviceProvider.fullName}
            />
          </Grid>
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <UniversalActivityLogTable objectId={paymentRecord.verification.id} />
      )}
    </>
  );
}
