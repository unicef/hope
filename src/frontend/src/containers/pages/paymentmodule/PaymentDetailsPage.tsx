import type { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ForceFailedButton } from '@components/paymentmodule/ForceFailedButton';
import { RevertForceFailedButton } from '@components/paymentmodule/RevertForceFailedButton';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { AdminButton } from '@core/AdminButton';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { PaymentStatusEnum } from '@restgenerated/models/PaymentStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import type { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { isPermissionDeniedError } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import PaymentDetails from '@components/paymentmodule/PaymentDetails/PaymentDetails';

function PaymentDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { paymentId } = useParams();
  const location = useLocation();
  const paymentListId = location.state?.parentId;

  const { baseUrl, businessArea, programId } = useBaseUrl();

  const {
    data: payment,
    isLoading: loading,
    error,
  } = useQuery<PaymentDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentListsPaymentsRetrieve,
      {
        businessAreaSlug: businessArea,
        paymentId: paymentId,
        programCode: programId,
        paymentListPk: paymentListId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentListsPaymentsRetrieve({
        businessAreaSlug: businessArea,
        paymentId: paymentId,
        programCode: programId,
        paymentListPk: paymentListId,
      }),
  });

  const paymentListStatus = payment?.parent?.status;
  const paymentListIsFollowUp = payment?.parent?.planType === 'FOLLOW_UP';
  const permissions = usePermissions();
  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied permission={PERMISSIONS.PM_VIEW_DETAILS} />;
  // The payment is missing whenever the request failed (404 for a payment of another
  // program, 5xx, network). Rendering nothing here used to leave a blank page.
  if (!payment)
    return (
      <SomethingWentWrong
        specificError={
          error?.message === 'Not Found'
            ? 'Payment has been removed or does not exist'
            : undefined
        }
        errorMessage={error?.message}
        goBackAddress={`/${baseUrl}/payment-module/payment-lists`}
      />
    );

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: '../payment-lists',
    },
    {
      title: ` ${paymentListIsFollowUp ? 'Follow-up ' : ''} Payment List ${
        payment?.parent?.unicefId
      }`,
      to: `/${baseUrl}/payment-module/${
        paymentListIsFollowUp ? 'followup-payment-lists' : 'payment-lists'
      }/${payment?.parent?.id}/`,
    },
  ];

  const renderButton = (): ReactElement | null => {
    if (
      hasPermissions(PERMISSIONS.PM_MARK_PAYMENT_AS_FAILED, permissions) &&
      (paymentListStatus === PaymentListStatusEnum.ACCEPTED ||
        paymentListStatus === PaymentListStatusEnum.FINISHED) &&
      !payment.parent?.isPaymentGateway
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
        title={`Payment ${payment?.unicefId}`}
        breadCrumbs={breadCrumbsItems}
        flags={<AdminButton adminUrl={payment?.adminUrl} />}
      >
        {renderButton()}
      </PageHeader>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
        }}
      >
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
