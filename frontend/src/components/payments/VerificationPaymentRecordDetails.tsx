import { Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import {
  formatCurrencyWithSymbol,
  paymentRecordStatusToColor,
  paymentStatusDisplayMap,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { PaymentRecordQuery } from '@generated/graphql';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import { BlackLink } from '@core/BlackLink';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Overview } from '@components/payments/Overview';
import { HouseholdDetails } from '@components/payments/HouseholdDetails';
import { useProgramContext } from '../../programContext';
import { IndividualDetails } from '@components/payments/IndividualDetails';

interface VerificationPaymentRecordDetailsProps {
  paymentRecord: PaymentRecordQuery['paymentRecord'];
  canViewActivityLog: boolean;
  choicesData;
}

export function VerificationPaymentRecordDetails({
  paymentRecord,
  canViewActivityLog,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  choicesData,
}: VerificationPaymentRecordDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();

  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Payment Record Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={paymentRecord.status}
                statusToColor={paymentRecordStatusToColor}
                statusNameMapping={paymentStatusDisplayMap}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Household')}>
              <BlackLink
                to={`/${baseUrl}/population/household/${paymentRecord.household.id}`}
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
          <Typography variant="h6">{t('Verification Details')}</Typography>
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
      {isSocialDctType ? (
        <IndividualDetails
          individual={paymentRecord.household.headOfHousehold}
        />
      ) : (
        <HouseholdDetails household={paymentRecord.household} />
      )}
      <Overview>
        <Title>
          <Typography variant="h6">{t('Entitlement Details')}</Typography>
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
              value={paymentRecord.deliveryType.name}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={
                <UniversalMoment>{paymentRecord.deliveryDate}</UniversalMoment>
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
