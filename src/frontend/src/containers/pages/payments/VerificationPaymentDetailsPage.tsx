import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { VerificationPaymentDetails } from '@components/payments/VerificationPaymentDetails';
import { VerifyManual } from '@components/payments/VerifyManual';
import { AdminButton } from '@core/AdminButton';
import {
  PaymentVerificationPlanStatus,
  usePaymentVerificationChoicesQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { PaymentPlan } from '@restgenerated/models/PaymentPlan';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { error } from 'console';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

function VerificationPaymentDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { paymentPlanId, paymentId } = useParams();
  const permissions = usePermissions();
  const { data: payment, isLoading: loading } = useQuery<PaymentPlan>({
    queryKey: ['payment', businessArea, paymentId, programId, paymentPlanId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsRetrieve2(
        {
          businessAreaSlug: businessArea,
          id: paymentPlanId,
          paymentId: paymentId,
          programSlug: programId,
        },
      ),
  });
  const { data: choicesData, loading: choicesLoading } =
    usePaymentVerificationChoicesQuery();
  const { baseUrl } = useBaseUrl();
  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!payment || !choicesData || permissions === null) return null;

  const { verificationPlans } = payment?.parent || {};
  const verificationPlansAmount = verificationPlans?.edges.length;
  const verification =
    verificationPlans.edges[verificationPlansAmount - 1].node;

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
      verification?.status !== PaymentVerificationPlanStatus.Finished ? (
        <VerifyManual
          paymentVerificationId={payment.verification?.id}
          status={payment.verification?.status}
          enabled={payment.verification.isManuallyEditable}
          receivedAmount={payment.verification.receivedAmount}
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
