import { Overview } from '@components/payments/Overview';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Typography } from '@mui/material';
import Grid from '@mui/material/Grid';
import { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import {
  formatCurrencyWithSymbol,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  safeStringify,
  verificationRecordsStatusToColor,
  formatFigure,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface PaymentDetailsProps {
  payment: PaymentDetail;
  canViewActivityLog: boolean;
  canViewHouseholdDetails: boolean;
}

export function PaymentDetails({
  payment,
  canViewActivityLog,
}: PaymentDetailsProps): ReactElement {
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { t } = useTranslation();
  let paymentVerification: PaymentDetail['verification'] = null;
  if (payment.verification && payment.verification.status !== 'PENDING') {
    paymentVerification = payment.verification;
  }

  const showFailureReason = [
    'NOT_DISTRIBUTED',
    'FORCE_FAILED',
    'TRANSACTION_ERRONEOUS',
  ].includes(payment.status);

  const collectorAccountData = payment?.snapshotCollectorAccountData ?? {};

  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
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
              label={t('ENTITLEMENT QUANTITY')}
              value={
                payment.entitlementQuantity != null
                  ? formatFigure(payment.entitlementQuantity)
                  : payment.entitlementQuantity
              }
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={
                payment.deliveredQuantity != null
                  ? formatFigure(payment.deliveredQuantity)
                  : payment.deliveredQuantity
              }
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('CURRENCY')} value={payment.currency} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={<UniversalMoment>{payment.deliveryDate}</UniversalMoment>}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('TARGET POPULATION')}>
              <BlackLink
                to={`/${businessArea}/programs/${programId}/target-population/${payment.parent.id}`}
              >
                {payment.parent?.name}
              </BlackLink>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Distribution Modality')}
              value={payment.parent?.deliveryMechanism?.name}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Original Payment Plan ID')}>
              {payment.parent && (
                <BlackLink
                  to={`/${baseUrl}/payment-module/${payment.parent.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${payment.parent.id}`}
                >
                  {payment.parent.unicefId}
                </BlackLink>
              )}
            </LabelizedField>
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      {paymentVerification != null ? (
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant="h6">{t('Verification Details')}</Typography>
          </Title>
          <Grid container spacing={3}>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('STATUS')}>
                <StatusBox
                  status={paymentVerification.status}
                  statusToColor={verificationRecordsStatusToColor}
                />
              </LabelizedField>
            </Grid>

            <Grid size={{ xs: 3 }}>
              <LabelizedField
                label={t('AMOUNT RECEIVED')}
                value={formatCurrencyWithSymbol(
                  paymentVerification.receivedAmount,
                  payment.currency,
                )}
              />
            </Grid>
          </Grid>
        </ContainerColumnWithBorder>
      ) : null}
      <Overview>
        <Title>
          <Typography variant="h6">{t('Entitlement Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('DELIVERY MECHANISM')}
              value={payment.deliveryMechanism?.name}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('FSP')} value={payment.fspName} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('TRANSACTION REFERENCE ID')}
              value={payment.transactionReferenceId}
            />
          </Grid>
        </Grid>
        <DividerLine />
        <Grid container spacing={3}>
          {Object.entries(collectorAccountData).map(([key, value]) => (
            <Grid key={key} size={{ xs: 3 }}>
              <LabelizedField
                label={t(`Account ${key}`)}
                value={safeStringify(value)}
              />
            </Grid>
          ))}
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant="h6">{t('Reconciliation Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t("Collector's Name")}
              value={payment.additionalCollectorName}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Document Type')}
              value={payment.additionalDocumentType}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Document Number')}
              value={payment.additionalDocumentNumber}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Extras')}
              value={payment.extras ? safeStringify(payment.extras) : '-'}
            />
          </Grid>
        </Grid>
        <DividerLine />
        <Grid container spacing={3}>
          {showFailureReason && (
            <Grid size={{ xs: 3 }}>
              <LabelizedField
                label={t('Failure Reason')}
                value={payment.reasonForUnsuccessfulPayment}
              />
            </Grid>
          )}
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <UniversalActivityLogTable objectId={payment.id} />
      )}
    </>
  );
}
