import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import {
  PaymentVerificationPlanStatus,
  usePaymentRecordQuery,
  usePaymentVerificationChoicesQuery,
} from '@generated/graphql';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { VerificationPaymentRecordDetails } from '@components/payments/VerificationPaymentRecordDetails';
import { VerifyManual } from '@components/payments/VerifyManual';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { AdminButton } from '@core/AdminButton';

export function VerificationPaymentRecordDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = usePaymentRecordQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const { data: choicesData, loading: choicesLoading } =
    usePaymentVerificationChoicesQuery();
  const { baseUrl } = useBaseUrl();
  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  const { paymentRecord } = data;
  if (!paymentRecord || !choicesData || permissions === null) return null;

  const { verificationPlans } = paymentRecord?.parent || {};
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
          title: `${t('Payment Plan')} ${paymentRecord.parent.unicefId}`,
          to: `/${baseUrl}/payment-verification/cash-plan/${paymentRecord.parent.id}`,
        },
      ]
      : []),
  ];

  const toolbar = (
    <PageHeader
      title={`${t('Payment Record ID')} ${paymentRecord.caId}`}
      breadCrumbs={breadCrumbsItems}
      flags={
        <AdminButton adminUrl={paymentRecord.verification?.adminUrl} />
      }
    >
      {verification?.verificationChannel === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) &&
      verification?.status !== PaymentVerificationPlanStatus.Finished ? (
        <VerifyManual
          paymentVerificationId={paymentRecord.verification.id}
          status={paymentRecord.verification?.status}
          enabled={paymentRecord.verification.isManuallyEditable}
          receivedAmount={paymentRecord.verification.receivedAmount}
        />
        ) : null}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <VerificationPaymentRecordDetails
        paymentRecord={paymentRecord}
        canViewActivityLog={hasPermissions(
          PERMISSIONS.ACTIVITY_LOG_VIEW,
          permissions,
        )}
        choicesData={choicesData}
      />
    </div>
  );
}
