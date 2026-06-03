import withErrorBoundary from '@components/core/withErrorBoundary';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { BatchDetailsHeader } from '@containers/pages/paymentmodule/Groups/BatchDetailsHeader';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

const BatchDetailsPage = (): ReactElement => {
  const { groupId, tag: rawTag } = useParams<{ groupId: string; tag: string }>();
  const tag = rawTag ? decodeURIComponent(rawTag) : '';
  const { t } = useTranslation();
  const [filter] = useState(initialFilter);
  const permissions = usePermissions();
  const { businessArea, programId } = useBaseUrl();

  const { data: group } = useQuery({
    queryKey: ['paymentPlanGroup', businessArea, programId, groupId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve({
        businessAreaSlug: businessArea,
        id: groupId,
        programCode: programId,
      }),
    enabled: !!groupId && !!businessArea && !!programId,
  });

  const exportFileLink =
    group?.batches.find((b) => String(b.exportTag) === tag)?.exportFileLink ??
    null;

  if (permissions === null) return null;
  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL, permissions)
  )
    return (
      <PermissionDenied
        permission={PERMISSIONS.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL}
      />
    );
  if (!groupId) return <LoadingComponent />;

  return (
    <>
      <BatchDetailsHeader groupId={groupId} tag={tag} exportFileLink={exportFileLink} />
      <TableWrapper>
        <PaymentPlansTable
          filter={filter}
          canViewDetails
          title={t('Payment Plans')}
          paymentPlanGroupId={groupId}
          tag={tag}
        />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(BatchDetailsPage, 'BatchDetailsPage');
