import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { VerificationRecordDetails } from '../../../components/payments/VerificationRecordDetails';
import { VerifyManual } from '../../../components/payments/VerifyManual';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { decodeIdString, isPermissionDeniedError } from '../../../utils/utils';
import {
  PaymentVerificationNode,
  usePaymentRecordVerificationQuery,
  usePaymentVerificationChoicesQuery,
} from '../../../__generated__/graphql';

export function VerificationRecordDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = usePaymentRecordVerificationQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = usePaymentVerificationChoicesQuery();
  const businessArea = useBusinessArea();
  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || permissions === null) return null;

  const paymentVerification = data.paymentRecordVerification as PaymentVerificationNode;
  const verification =
    paymentVerification.paymentRecord?.cashPlan?.verifications?.edges[0].node;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    ...(hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions)
      ? [
          {
            title: t('Payment Verification'),
            to: `/${businessArea}/payment-verification`,
          },
        ]
      : []),
    ...(hasPermissions(
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
      permissions,
    )
      ? [
          {
            title: `${t('Cash Plan')} ${decodeIdString(
              paymentVerification.paymentRecord.parent.id,
            )}`,
            to: `/${businessArea}/payment-verification/${paymentVerification.paymentRecord.parent.id}`,
          },
        ]
      : []),
  ];

  const toolbar = (
    <PageHeader
      title={`${t('Payment ID')} ${paymentVerification.paymentRecord.caId}`}
      breadCrumbs={breadCrumbsItems}
    >
      {verification.verificationChannel === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) ? (
        <VerifyManual
          paymentVerificationId={paymentVerification.id}
          enabled={paymentVerification.isManuallyEditable}
        />
      ) : null}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <VerificationRecordDetails
        paymentVerification={paymentVerification}
        canViewActivityLog={hasPermissions(
          PERMISSIONS.ACTIVITY_LOG_VIEW,
          permissions,
        )}
        choicesData={choicesData}
      />
    </div>
  );
}
