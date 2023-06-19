import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { VerificationPaymentDetails } from '../../../components/payments/VerificationPaymentDetails';
import { VerifyManual } from '../../../components/payments/VerifyManual';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { decodeIdString, isPermissionDeniedError } from '../../../utils/utils';
import {
  PaymentVerificationPlanStatus,
  usePaymentQuery,
  usePaymentVerificationChoicesQuery,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export function VerificationPaymentDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = usePaymentQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = usePaymentVerificationChoicesQuery();
  const { baseUrl } = useBaseUrl();
  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || permissions === null) return null;

  const { payment } = data;

  const verification = payment.parent?.verificationPlans?.edges[0].node;
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
            title: `${t('Payment Plan')} ${decodeIdString(payment.parent.id)}`,
            to: `/${baseUrl}/payment-verification/payment-plan/${payment.parent.id}`,
          },
        ]
      : []),
  ];

  const toolbar = (
    <PageHeader
      title={`${t('Payment ID')} ${payment.unicefId}`}
      breadCrumbs={breadCrumbsItems}
    >
      {verification.verificationChannel === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) &&
      verification.status !== PaymentVerificationPlanStatus.Finished ? (
        <VerifyManual paymentVerificationId={payment.verification.id} enabled />
      ) : null}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <VerificationPaymentDetails
        payment={payment}
        canViewActivityLog={hasPermissions(
          PERMISSIONS.ACTIVITY_LOG_VIEW,
          permissions,
        )}
        choicesData={choicesData}
      />
    </div>
  );
}
