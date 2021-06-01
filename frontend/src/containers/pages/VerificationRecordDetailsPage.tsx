import React from 'react';
import { useParams } from 'react-router-dom';
import {
  PaymentVerificationNode,
  usePaymentRecordVerificationQuery,
} from '../../__generated__/graphql';
import { PageHeader } from '../../components/PageHeader';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { VerificationRecordDetails } from '../../components/payments/VerificationRecordDetails';
import { decodeIdString, isPermissionDeniedError } from '../../utils/utils';
import { VerifyManual } from '../../components/payments/VerifyManual';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

export function VerificationRecordDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = usePaymentRecordVerificationQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();
  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || permissions === null) return null;

  const paymentVerification = data.paymentRecordVerification as PaymentVerificationNode;
  const verification =
    paymentVerification.paymentRecord?.cashPlan?.verifications?.edges[0].node;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    ...(hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions)
      ? [
          {
            title: 'Payment Verification',
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
            title: `Cash Plan ${decodeIdString(
              paymentVerification.paymentRecord.cashPlan.id,
            )}`,
            to: `/${businessArea}/payment-verification/${paymentVerification.paymentRecord.cashPlan.id}`,
          },
        ]
      : []),
  ];

  const toolbar = (
    <PageHeader
      title={`Payment ID ${paymentVerification.paymentRecord.caId}`}
      breadCrumbs={breadCrumbsItems}
    >
      {verification.verificationMethod === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) ? (
        <VerifyManual paymentVerificationId={paymentVerification.id} enabled={paymentVerification.isManuallyEditable}/>
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
      />
    </div>
  );
}
