import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { useBusinessArea } from '@hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  getPhoneNoLabel,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import { Overview } from '@components/payments/Overview';

interface PaymentDetailsProps {
  payment: PaymentDetail;
  canViewActivityLog: boolean;
  canViewHouseholdDetails: boolean;
}

export function PaymentDetails({
  payment,
  canViewActivityLog,
  canViewHouseholdDetails,
}: PaymentDetailsProps): ReactElement {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  let paymentVerification: PaymentDetail['verification'] = null;
  if (payment.verification && payment.verification.status !== 'PENDING') {
    paymentVerification = payment.verification;
  }

  const showFailureReason = [
    'NOT_DISTRIBUTED',
    'FORCE_FAILED',
    'TRANSACTION_ERRONEOUS',
  ].includes(payment.status);

  const collectorAccountData = payment?.snapshotCollectorAccountData
  ? JSON.parse(payment.snapshotCollectorAccountData)
  : {};

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
              label={t('DISTRIBUTION MODALITY')}
              value={payment.parent?.unicefId}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Related Payment Id')}
              value={payment.sourcePayment?.unicefId}
            />
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
          <Typography variant="h6">{beneficiaryGroup?.groupLabel}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={`${beneficiaryGroup?.groupLabel} ID`}>
              {payment.household?.id && canViewHouseholdDetails ? (
                <BlackLink
                  to={`/${businessArea}/programs/${programId}/population/household/${payment.household.id}`}
                >
                  {payment.household.unicefId}
                </BlackLink>
              ) : (
                <div>
                  {payment.household?.id ? payment.household.unicefId : '-'}
                </div>
              )}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t("Collector's Name")}
              value={payment.snapshotCollectorFullName}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t("Collector's ID")}
              value={payment.collector?.unicefId}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('TOTAL PERSON COVERED')}
              value={payment.household.size}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('PHONE NUMBER')}
              value={getPhoneNoLabel(
                payment.collector.phoneNo,
                payment.collector.phoneNoValid,
              )}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('ALT. PHONE NUMBER')}
              value={getPhoneNoLabel(
                payment.collector.phoneNoAlternative,
                payment.collector.phoneNoAlternativeValid,
              )}
            />
          </Grid>
        </Grid>
      </Overview>
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
                value={String(value)}
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
