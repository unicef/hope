import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  PaymentPlanStatus,
  PaymentStatus,
  useCashAssistUrlPrefixQuery,
  usePaymentQuery,
} from '../../../__generated__/graphql';
import { PaymentDetails } from '../../../components/paymentmodule/PaymentDetails';
import { RevertForceFailedButton } from '../../../components/paymentmodule/RevertForceFailedButton';
import { ForceFailedButton } from '../../../components/paymentmodule/ForceFailedButton';

export const PaymentDetailsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  const { data, loading } = usePaymentQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const paymentPlanStatus = data?.payment?.parent?.status;
  const paymentPlanIsFollowUp = data?.payment?.parent?.isFollowUp;
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  if (loading || caLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  if (!data || !caData) return null;
  const { payment } = data;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/`,
    },
    {
      title: ` ${paymentPlanIsFollowUp ? 'Follow-up ' : null} Payment Plan ${
        payment.parent.unicefId
      }`,
      to: `/${businessArea}/payment-module/${
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

  return (
    <>
      <PageHeader
        title={`Payment ${payment.unicefId}`}
        breadCrumbs={breadCrumbsItems}
      >
        {renderButton()}
      </PageHeader>
      <Box display='flex' flexDirection='column'>
        <PaymentDetails
          payment={payment}
          canViewActivityLog={hasPermissions(
            PERMISSIONS.ACTIVITY_LOG_VIEW,
            permissions,
          )}
        />
      </Box>
    </>
  );
};
