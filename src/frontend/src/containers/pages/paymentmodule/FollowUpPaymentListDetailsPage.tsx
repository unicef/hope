import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FollowUpPaymentListDetails } from '@components/paymentmodule/FollowUpPaymentListDetails/FollowUpPaymentListDetails';
import { FollowUpPaymentListDetailsHeader } from '@components/paymentmodule/FollowUpPaymentListDetails/FollowUpPaymentListDetailsHeader';
import { PaymentListAcceptanceProcess } from '@components/paymentmodule/PaymentListDetails/AcceptanceProcess/PaymentListAcceptanceProcess';
import ExcludeSection from '@components/paymentmodule/PaymentListDetails/ExcludeSection/ExcludeSection';
import { PaymentListDetailsResults } from '@components/paymentmodule/PaymentListDetails/PaymentListDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentListDetails/ReconciliationSummary';
import PaymentsTable from '@containers/tables/paymentmodule/PaymentsTable/PaymentsTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { PAYMENT_LIST_BACKGROUND_ACTION_ERROR_STATUSES } from '@utils/constants';
import { isPermissionDeniedError } from '@utils/utils';
import type { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';

export function FollowUpPaymentListDetailsPage(): ReactElement {
  const { paymentListId } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { data: paymentList, error } = useQuery<PaymentListDetail>({
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
    refetchIntervalInBackground: true,
  });

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied permission={PERMISSIONS.PM_VIEW_DETAILS} />;
  if (!paymentList) return null;

  const { status } = paymentList;

  const shouldDisplayReconciliationSummary =
    status === PaymentListStatusEnum.ACCEPTED ||
    status === PaymentListStatusEnum.FINISHED ||
    status === PaymentListStatusEnum.READY_FOR_CLOSURE ||
    status === PaymentListStatusEnum.CLOSED;

  if (!paymentList) return null;

  return (
    <>
      <FollowUpPaymentListDetailsHeader
        paymentList={paymentList}
        baseUrl={baseUrl}
        permissions={permissions}
      />
      <FollowUpPaymentListDetails baseUrl={baseUrl} paymentList={paymentList} />
      <PaymentListAcceptanceProcess paymentList={paymentList} />
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
        <UniversalActivityLogTable objectId={paymentList.id} />
      )}
    </>
  );
}
export default withErrorBoundary(
  FollowUpPaymentListDetailsPage,
  'FollowUpPaymentListDetailsPage',
);
