import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ForceFailedButton } from '@components/paymentmodule/ForceFailedButton';
import { RevertForceFailedButton } from '@components/paymentmodule/RevertForceFailedButton';
import { PaymentDetails } from '@components/paymentmodulepeople/PaymentDetails';
import { AdminButton } from '@core/AdminButton';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PaymentStatusEnum } from '@restgenerated/models/PaymentStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

export const PeoplePaymentDetailsPage = (): ReactElement => {
  const { t } = useTranslation();
  const { paymentPlanId, paymentId } = useParams();
  const { businessArea, programId } = useBaseUrl();
  const { data: payment, isLoading: loading } = useQuery<PaymentDetail>({
    queryKey: [
      'paymentPlan',
      businessArea,
      paymentId,
      programId,
      paymentPlanId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsRetrieve({
        businessAreaSlug: businessArea,
        paymentId: paymentId,
        programSlug: programId,
        paymentPlanId,
      }),
  });
  const paymentPlanStatus = payment?.parent?.status;
  const paymentPlanIsFollowUp = payment?.parent?.isFollowUp;
  const permissions = usePermissions();
  const { baseUrl } = useBaseUrl();
  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  if (!payment) return null;
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
        paymentPlanStatus === PaymentPlanStatusEnum.ACCEPTED) ||
      paymentPlanStatus === PaymentPlanStatusEnum.FINISHED
    ) {
      const ButtonComponent =
        payment.status === PaymentStatusEnum.FORCE_FAILED
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
};
export default withErrorBoundary(
  PeoplePaymentDetailsPage,
  'PeoplePaymentDetailsPage',
);
