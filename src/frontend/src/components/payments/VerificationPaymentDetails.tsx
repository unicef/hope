import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import {
  formatCurrencyWithSymbol,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { PaymentQuery } from '@generated/graphql';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import { Title } from '@core/Title';
import { Overview } from '@components/payments/Overview';
import { HouseholdDetails } from '@components/payments/HouseholdDetails';
import { useProgramContext } from '../../programContext';
import { IndividualDetails } from '@components/payments/IndividualDetails';
import { ReactElement } from 'react';

interface VerificationPaymentDetailsProps {
  payment: PaymentQuery['payment'];
  canViewActivityLog: boolean;
}

export function VerificationPaymentDetails({
  payment,
  canViewActivityLog,
}: VerificationPaymentDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { isSocialDctType } = useProgramContext();

  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Payment Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.status}
                statusToColor={paymentStatusToColor}
                statusNameMapping={paymentStatusDisplayMap}
              />
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('TARGET POPULATION')}
              value={payment.parent.name}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DISTRIBUTION MODALITY')}
              value={payment.distributionModality}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Verification Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.verification.status}
                statusToColor={verificationRecordsStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('AMOUNT RECEIVED')}
              value={formatCurrencyWithSymbol(
                payment.verification.receivedAmount,
                payment.currency,
              )}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      {isSocialDctType ? (
        <IndividualDetails individual={payment.household.headOfHousehold} />
      ) : (
        <HouseholdDetails household={payment.household} />
      )}
      <Overview>
        <Title>
          <Typography variant="h6">{t('Entitlement Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('ENTITLEMENT QUANTITY')}
              value={payment.entitlementQuantity}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={payment.deliveredQuantity}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('CURRENCY')} value={payment.currency} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DELIVERY TYPE')}
              value={payment.deliveryType?.name}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={<UniversalMoment>{payment.deliveryDate}</UniversalMoment>}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('FSP')}
              value={payment.serviceProvider.fullName}
            />
          </Grid>
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <UniversalActivityLogTable
          objectId={payment.parent.verificationPlans.edges[0].node.id}
        />
      )}
    </>
  );
}
