import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ForceFailedButton } from '@components/paymentmodule/ForceFailedButton';
import { RevertForceFailedButton } from '@components/paymentmodule/RevertForceFailedButton';
import { AdminButton } from '@core/AdminButton';
import {
  PaymentPlanStatus,
  PaymentStatus,
  useCashAssistUrlPrefixQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PaymentDetails } from '@components/paymentmodulepeople/PaymentDetails';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

function PaymentDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { paymentId } = useParams();
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  const { businessArea, programId } = useBaseUrl();

  const { data: payment, isLoading: loading } = useQuery({
    queryKey: ['paymentPlan', businessArea, paymentId, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug: businessArea,
        id: paymentId,
        programSlug: programId,
      }),
  });

  const paymentPlanStatus = payment.parent?.status;
  const paymentPlanIsFollowUp = payment.parent?.is_follow_up;
  const permissions = usePermissions();
  const { baseUrl } = useBaseUrl();
  if (loading || caLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  if (!payment || !caData) return null;
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
      }/${payment.parent.id}/`,
    },
  ];

  const renderButton = (): ReactElement | null => {
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
        title={`Payment ${payment.unicef_id}`}
        breadCrumbs={breadCrumbsItems}
        flags={<AdminButton adminUrl={payment.admin_url} />}
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
export default withErrorBoundary(PaymentDetailsPage, 'PaymentDetailsPage');
