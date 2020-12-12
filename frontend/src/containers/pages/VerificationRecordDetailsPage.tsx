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
import { decodeIdString } from '../../utils/utils';
import { VerifyManual } from '../../components/payments/VerifyManual';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

export function VerificationRecordDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading } = usePaymentRecordVerificationQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();
  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
      permissions,
    )
  )
    return <PermissionDenied />;
  if (!data) return null;

  const paymentVerification = data.paymentRecordVerification as PaymentVerificationNode;
  const verification =
    paymentVerification.paymentRecord?.cashPlan?.verifications?.edges[0].node;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${businessArea}/payment-verification/`,
    },
    {
      title: `Cash Plan ${decodeIdString(
        paymentVerification.paymentRecord.cashPlan.id,
      )}`,
      to: `/${businessArea}/payment-verification/${paymentVerification.paymentRecord.cashPlan.id}`,
    },
  ];

  const toolbar = (
    <PageHeader
      title={`Payment ID ${decodeIdString(
        paymentVerification.paymentRecord.id,
      )}`}
      breadCrumbs={breadCrumbsItems}
    >
      {verification.verificationMethod === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) ? (
        <VerifyManual paymentVerificationId={paymentVerification.id} />
      ) : null}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <VerificationRecordDetails paymentVerification={paymentVerification} />
    </div>
  );
}
