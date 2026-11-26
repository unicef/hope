import withErrorBoundary from '@components/core/withErrorBoundary';
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
import type { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import {
  formatCurrencyCode,
  formatCurrencyWithSymbol,
  formatFigure,
  formatNormalCaseValue,
  getPhoneNoLabel,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  safeStringify,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface PaymentDetailsProps {
  payment: PaymentDetail;
  canViewActivityLog: boolean;
  canViewHouseholdDetails: boolean;
}

function PaymentDetails({
  payment,
  canViewActivityLog,
  canViewHouseholdDetails,
}: PaymentDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { selectedProgram, isSocialDctType } = useProgramContext();
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

  const collectorAccountData = payment?.snapshotCollectorAccountData ?? {};
  const extraFields = Object.entries(payment.extraFields ?? {});
  const fspExtraFields = Object.entries(payment.fspExtraFields ?? {});

  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
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
              label={t('DELIVERY DATE')}
              value={<UniversalMoment>{payment.deliveryDate}</UniversalMoment>}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('TARGET POPULATION')}>
              <BlackLink
                to={`/${businessArea}/programs/${programId}/target-population/${payment.parent.id}`}
              >
                {payment.parent?.name}
              </BlackLink>
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Distribution Modality')}
              value={payment.parent?.deliveryMechanism?.name}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Original Payment Plan ID')}>
              {payment.parent && (
                <BlackLink
                  to={`/${baseUrl}/payment-module/${payment.parent.planType === 'FOLLOW_UP' ? 'followup-payment-plans' : 'payment-plans'}/${payment.parent.id}`}
                >
                  {payment.parent.unicefId}
                </BlackLink>
              )}
            </LabelizedField>
          </ResponsiveGrid>
          {payment.parent.isPaymentGateway && (
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t('Sent to FSP on')}
                value={
                  <UniversalMoment>{payment.sentToFspDate}</UniversalMoment>
                }
              />
            </ResponsiveGrid>
          )}
        </ResponsiveGridContainer>
      </ContainerColumnWithBorder>
      {paymentVerification != null ? (
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant="h6">{t('Verification Details')}</Typography>
          </Title>
          <ResponsiveGridContainer spacing={3}>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('STATUS')}>
                <StatusBox
                  status={paymentVerification.status}
                  statusToColor={verificationRecordsStatusToColor}
                />
              </LabelizedField>
            </ResponsiveGrid>

            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t('AMOUNT RECEIVED')}
                value={formatCurrencyWithSymbol(
                  paymentVerification.receivedAmount,
                  payment.currency,
                  payment.currencyVisionCode,
                )}
              />
            </ResponsiveGrid>
          </ResponsiveGridContainer>
        </ContainerColumnWithBorder>
      ) : null}
      {isSocialDctType && (
        <Overview>
          <Title>
            <Typography variant="h6">{beneficiaryGroup?.groupLabel}</Typography>
          </Title>
          <ResponsiveGridContainer spacing={3}>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={`${beneficiaryGroup?.groupLabel}`}>
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
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t("Collector's Name")}
                value={payment.snapshotCollectorFullName}
              />
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t("Collector's ID")}
                value={payment.collector?.unicefId}
              />
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t('TOTAL PERSON COVERED')}
                value={payment.household.size}
              />
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t('PHONE NUMBER')}
                value={getPhoneNoLabel(
                  payment.collector.phoneNo,
                  payment.collector.phoneNoValid,
                )}
              />
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField
                label={t('ALT. PHONE NUMBER')}
                value={getPhoneNoLabel(
                  payment.collector.phoneNoAlternative,
                  payment.collector.phoneNoAlternativeValid,
                )}
              />
            </ResponsiveGrid>
          </ResponsiveGridContainer>
        </Overview>
      )}
      <Overview>
        <Title>
          <Typography variant="h6">{t('Entitlement Details')}</Typography>
        </Title>
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('DELIVERY MECHANISM')}
              value={payment.deliveryMechanism?.name}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('FSP')} value={payment.fspName} />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('TRANSACTION REFERENCE ID')}
              value={payment.transactionReferenceId}
            />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
        <DividerLine />
        <ResponsiveGridContainer spacing={3}>
          {Object.entries(collectorAccountData).map(([key, value]) => (
            <ResponsiveGrid key={key} size="quarter">
              <LabelizedField
                label={t(`Account ${key}`)}
                value={safeStringify(value)}
              />
            </ResponsiveGrid>
          ))}
        </ResponsiveGridContainer>
      </Overview>
      <Overview>
        <Title>
          <Typography variant="h6">{t('Reconciliation Details')}</Typography>
        </Title>
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter">
            <LabelizedField
              label={t("Collector's Name")}
              value={payment.additionalCollectorName}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter">
            <LabelizedField
              label={t('Document Type')}
              value={payment.additionalDocumentType}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter">
            <LabelizedField
              label={t('Document Number')}
              value={payment.additionalDocumentNumber}
            />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
        <DividerLine />
        <ResponsiveGridContainer spacing={3}>
          {showFailureReason && (
            <ResponsiveGrid size="quarter">
              <LabelizedField
                label={t('Failure Reason')}
                value={payment.reasonForUnsuccessfulPayment}
              />
            </ResponsiveGrid>
          )}
        </ResponsiveGridContainer>
      </Overview>
      {extraFields.length > 0 && (
        <Overview>
          <Title>
            <Typography variant="h6">
              {t('Reconciliation Information: Extra Info')}
            </Typography>
          </Title>
          <ResponsiveGridContainer spacing={3}>
            {extraFields.map(([key, value]) => (
              <ResponsiveGrid key={key} size="quarter">
                <LabelizedField
                  label={formatNormalCaseValue(key)}
                  value={safeStringify(value)}
                />
              </ResponsiveGrid>
            ))}
          </ResponsiveGridContainer>
        </Overview>
      )}
      {fspExtraFields.length > 0 && (
        <Overview>
          <Title>
            <Typography variant="h6">{t('FSP extra fields')}</Typography>
          </Title>
          <ResponsiveGridContainer spacing={3}>
            {fspExtraFields.map(([key, value]) => (
              <ResponsiveGrid key={key} size="quarter">
                <LabelizedField
                  label={formatNormalCaseValue(key)}
                  value={safeStringify(value)}
                />
              </ResponsiveGrid>
            ))}
          </ResponsiveGridContainer>
        </Overview>
      )}
      {canViewActivityLog && (
        <UniversalActivityLogTable objectId={payment.id} />
      )}
    </>
  );
}
export default withErrorBoundary(PaymentDetails, 'PaymentDetails');
