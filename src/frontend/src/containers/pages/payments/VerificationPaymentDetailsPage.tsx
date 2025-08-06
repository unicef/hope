import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { VerificationPaymentDetails } from '@components/payments/VerificationPaymentDetails';
import { VerifyManual } from '@components/payments/VerifyManual';
import { AdminButton } from '@core/AdminButton';
import { PaymentVerificationPlanStatusEnum } from '@restgenerated/models/PaymentVerificationPlanStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PaymentDetail } from '@restgenerated/models/PaymentDetail';

function VerificationPaymentDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { paymentPlanId, id } = useParams();
  const permissions = usePermissions();
  const {
    data: payment,
    isLoading: loading,
    error,
  } = useQuery<PaymentDetail>({
    queryKey: ['payment', businessArea, id, programId, paymentPlanId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsRetrieve(
        {
          businessAreaSlug: businessArea,
          paymentVerificationPk: paymentPlanId,
          id,
          programSlug: programId,
        },
      ),
  });
  const { baseUrl } = useBaseUrl();
  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!payment || permissions === null) return null;

  const { paymentVerificationPlans } = payment?.parent || {};
  const verificationPlansAmount = paymentVerificationPlans?.length;
  const verification = paymentVerificationPlans[verificationPlansAmount - 1];

  const breadCrumbsItems: BreadCrumbsItem[] = [
    ...(hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions)
      ? [
          {
            title: t('Payment Verification'),
            to: `/${baseUrl}/payment-verification`,
          },
        ]
      : []),
    ...(hasPermissions(
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
      permissions,
    )
      ? [
          {
            title: `${t('Payment Plan')} ${payment.parent.unicefId}`,
            to: `/${baseUrl}/payment-verification/payment-plan/${payment.parent.id}`,
          },
        ]
      : []),
  ];

  const toolbar = (
    <PageHeader
      title={`${t('Payment ID')} ${payment.unicefId}`}
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={payment.verification?.adminUrl} />}
    >
      {verification?.verificationChannel === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) &&
      verification?.status !== PaymentVerificationPlanStatusEnum.FINISHED ? (
        <VerifyManual
          paymentVerificationId={payment.verification?.id}
          status={payment.verification?.status}
          enabled={payment.verification.isManuallyEditable}
          receivedAmount={payment.verification.receivedAmount}
          paymentId={payment.id}
          paymentPlanId={paymentPlanId}
          verificationPlanId={paymentPlanId}
        />
      ) : null}
    </PageHeader>
  );
  return (
    <>
      {toolbar}
      <VerificationPaymentDetails
        payment={payment}
        canViewActivityLog={hasPermissions(
          PERMISSIONS.ACTIVITY_LOG_VIEW,
          permissions,
        )}
      />
    </>
  );
}

export default withErrorBoundary(
  VerificationPaymentDetailsPage,
  'VerificationPaymentDetailsPage',
);
