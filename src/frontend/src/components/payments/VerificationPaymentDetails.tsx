import { Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import {
  formatCurrencyCode,
  formatCurrencyWithSymbol,
  formatFigure,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import { Title } from '@core/Title';
import { Overview } from '@components/payments/Overview';
import { HouseholdDetails } from '@components/payments/HouseholdDetails';
import { useProgramContext } from '../../programContext';
import { IndividualDetails } from '@components/payments/IndividualDetails';
import type { ReactElement } from 'react';
import type { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface VerificationPaymentDetailsProps {
  payment: PaymentDetail;
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
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.status}
                statusToColor={paymentStatusToColor}
                statusNameMapping={paymentStatusDisplayMap}
              />
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('TARGET POPULATION')}
              value={payment.parent.name}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('DISTRIBUTION MODALITY')}
              value={payment.parent?.deliveryMechanism?.name}
            />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </ContainerColumnWithBorder>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Verification Details')}</Typography>
        </Title>
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.verification.status}
                statusToColor={verificationRecordsStatusToColor}
              />
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('AMOUNT RECEIVED')}
              value={formatCurrencyWithSymbol(
                payment.verification.receivedAmount,
                payment.currency,
                payment.currencyVisionCode,
              )}
            />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
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
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('ENTITLEMENT QUANTITY')}
              value={formatFigure(payment.entitlementQuantity)}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={formatFigure(payment.deliveredQuantity)}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('CURRENCY')}
              value={formatCurrencyCode(
                payment.currency,
                payment.currencyVisionCode,
              )}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('DELIVERY TYPE')}
              value={payment.deliveryMechanism?.name}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={<UniversalMoment>{payment.deliveryDate}</UniversalMoment>}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('FSP')} value={payment.fspName} />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </Overview>
      {canViewActivityLog && (
        <UniversalActivityLogTable
          objectId={payment.parent.paymentVerificationPlans[0].id}
        />
      )}
    </>
  );
}
