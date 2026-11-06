import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentListDetailsResults } from '@components/paymentmodule/PaymentListDetails/PaymentListDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentListDetails/ReconciliationSummary';
import { PaymentListDetails } from '@containers/pages/paymentmodule/ProgramCycle/PaymentListDetails/PaymentListDetails';
import { PaymentListDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/PaymentListDetails/PaymentListDetailsHeader';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { isPermissionDeniedError } from '@utils/utils';
import type { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import PaymentsTable from '@containers/tables/paymentmodule/PaymentsTable/PaymentsTable';
import ExcludeSection from '@components/paymentmodule/PaymentListDetails/ExcludeSection/ExcludeSection';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { PAYMENT_LIST_BACKGROUND_ACTION_ERROR_STATUSES } from '@utils/constants';
import { RestService } from '@restgenerated/services/RestService';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import Entitlement from '@components/paymentmodule/PaymentListDetails/Entitlement/Entitlement';
import { PaymentListAcceptanceProcess } from '@components/paymentmodule/PaymentListDetails/AcceptanceProcess/PaymentListAcceptanceProcess';
import PaymentVerificationSummarySection from '@components/paymentmodule/PaymentListDetails/PaymentVerificationSummarySection/PaymentVerificationSummarySection';

const PaymentListDetailsPage = (): ReactElement => {
  const { paymentListId } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const {
    data: paymentList,
    isLoading,
    error,
  } = useQuery<PaymentListDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentListsRetrieve,
      {
        businessAreaSlug: businessArea,
        id: paymentListId,
        programCode: programId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentListsRetrieve({
        businessAreaSlug: businessArea,
        id: paymentListId,
        programCode: programId,
      }),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data?.backgroundActionStatus !== null &&
        !PAYMENT_LIST_BACKGROUND_ACTION_ERROR_STATUSES.includes(
          data?.backgroundActionStatus,
        )
      ) {
        return 3000;
      }
      return false;
    },
  });

  if (isLoading) return <LoadingComponent />;
  if (permissions === null || !paymentList) return null;

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied permission={PERMISSIONS.PM_VIEW_DETAILS} />;
  if (!paymentList) return null;

  const { status } = paymentList;

  const shouldDisplayEntitlement = status !== PaymentListStatusEnum.OPEN;

  const shouldDisplayReconciliationSummary =
    status === PaymentListStatusEnum.ACCEPTED ||
    status === PaymentListStatusEnum.FINISHED ||
    status === PaymentListStatusEnum.READY_FOR_CLOSURE ||
    status === PaymentListStatusEnum.CLOSED;

  const shouldDisplayVerificationSummary =
    status === PaymentListStatusEnum.FINISHED ||
    status === PaymentListStatusEnum.READY_FOR_CLOSURE ||
    status === PaymentListStatusEnum.CLOSED;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <PaymentListDetailsHeader
        paymentList={paymentList}
        permissions={permissions}
      />
      <PaymentListDetails baseUrl={baseUrl} paymentList={paymentList} />
      <PaymentListAcceptanceProcess paymentList={paymentList} />
      {shouldDisplayVerificationSummary && (
        <PaymentVerificationSummarySection paymentList={paymentList} />
      )}
      {shouldDisplayEntitlement && (
        <Entitlement paymentList={paymentList} permissions={permissions} />
      )}
      <ExcludeSection paymentList={paymentList} />
      <PaymentListDetailsResults paymentList={paymentList} />
      <PaymentsTable
        businessArea={businessArea}
        paymentList={paymentList}
        permissions={permissions}
        canViewDetails
      />
      {shouldDisplayReconciliationSummary && (
        <ReconciliationSummary paymentList={paymentList} />
      )}
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentList?.id} />
      )}
    </Box>
  );
};

export default withErrorBoundary(
  PaymentListDetailsPage,
  'PaymentListDetailsPage',
);
