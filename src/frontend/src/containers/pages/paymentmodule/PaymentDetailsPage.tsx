import { Box } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import {
  PaymentPlanStatus,
  PaymentStatus,
  useCashAssistUrlPrefixQuery,
  usePaymentQuery,
} from '@generated/graphql';
import { PaymentDetails } from '@components/paymentmodule/PaymentDetails';
import { RevertForceFailedButton } from '@components/paymentmodule/RevertForceFailedButton';
import { ForceFailedButton } from '@components/paymentmodule/ForceFailedButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AdminButton } from '@core/AdminButton';

export function PaymentDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { paymentId } = useParams();
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  const { data, loading } = usePaymentQuery({
    variables: { id: paymentId },
    fetchPolicy: 'cache-and-network',
  });
  const paymentPlanStatus = data?.payment?.parent?.status;
  const paymentPlanIsFollowUp = data?.payment?.parent?.isFollowUp;
  const permissions = usePermissions();
  const { baseUrl } = useBaseUrl();
  if (loading || caLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  if (!data || !caData) return null;
  const { payment } = data;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
    {
      title: ` ${paymentPlanIsFollowUp ? 'Follow-up ' : ''} Payment Plan ${
        payment.parent.unicefId
      }`,
      to: `/${baseUrl}/payment-module/${
        paymentPlanIsFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${data.payment.parent.id}/`,
    },
  ];

  const renderButton = (): React.ReactElement | null => {
    if (
      (hasPermissions(PERMISSIONS.PM_MARK_PAYMENT_AS_FAILED, permissions) &&
        paymentPlanStatus === PaymentPlanStatus.Accepted) ||
      paymentPlanStatus === PaymentPlanStatus.Finished
    ) {
      const ButtonComponent =
        payment.status === PaymentStatus.ForceFailed
          ? RevertForceFailedButton
          : ForceFailedButton;
      return <ButtonComponent paymentId={payment.id} />;
    }
    return null;
  };

  const canViewHouseholdDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    permissions,
  );

  return (
    <>
      <PageHeader
        title={`Payment ${payment.unicefId}`}
        breadCrumbs={breadCrumbsItems}
        flags={<AdminButton adminUrl={payment.adminUrl} />}
      >
        {renderButton()}
      </PageHeader>
      <Box display="flex" flexDirection="column">
        <PaymentDetails
          payment={payment}
          canViewActivityLog={hasPermissions(
            PERMISSIONS.ACTIVITY_LOG_VIEW,
            permissions,
          )}
          canViewHouseholdDetails={canViewHouseholdDetails}
        />
      </Box>
    </>
  );
}
