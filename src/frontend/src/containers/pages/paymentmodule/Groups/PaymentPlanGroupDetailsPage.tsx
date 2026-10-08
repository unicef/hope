import withErrorBoundary from '@components/core/withErrorBoundary';
import AcceptanceProcess from '@components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { PermissionDenied } from '@core/PermissionDenied';
import { TableWrapper } from '@core/TableWrapper';
import { Title } from '@core/Title';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { Grid, Typography } from '@mui/material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { PaymentPlanGroupDetailsHeader } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupDetailsHeader';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { isGroupBackgroundActionBusy } from './utils';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

const PaymentPlanGroupDetailsPage = (): ReactElement => {
  const { groupId } = useParams<{ groupId: string }>();
  const { businessArea, programId, baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const [filter] = useState(initialFilter);
  const permissions = usePermissions();
  const queryClient = useQueryClient();
  const { data: group, isLoading } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
      {
        businessAreaSlug: businessArea,
        id: groupId,
        programCode: programId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve({
        businessAreaSlug: businessArea,
        id: groupId,
        programCode: programId,
      }),
    enabled: !!groupId && !!businessArea && !!programId,
    // Poll while the group is exporting/importing an XLSX so the page reflects
    // the result (export_file populated, status cleared) without a manual refresh.
    refetchInterval: (query) =>
      isGroupBackgroundActionBusy(query.state.data ?? null) ? 3000 : false,
    refetchIntervalInBackground: true,
  });

  const wasBusy = useRef(false);
  useEffect(() => {
    const isBusy = isGroupBackgroundActionBusy(group ?? null);
    if (wasBusy.current && !isBusy) {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
      });
    }
    wasBusy.current = isBusy;
  }, [group, queryClient]);

  if (permissions === null) return null;
  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL, permissions)
  )
    return (
      <PermissionDenied
        permission={PERMISSIONS.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL}
      />
    );
  if (isLoading) return <LoadingComponent />;

  return (
    <>
      <PaymentPlanGroupDetailsHeader group={group} />
      <Grid size={{ xs: 12 }}>
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant="h6">{t('Details')}</Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Name')}>
                  {group?.name ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Cycle')}>
                  {group?.cycle ? (
                    <BlackLink
                      to={`/${baseUrl}/payment-module/program-cycles/${group.cycle.id}`}
                    >
                      {group.cycle.title}
                    </BlackLink>
                  ) : (
                    '-'
                  )}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('FSP')}>
                  {group?.financialServiceProvider?.name ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Currency')}>
                  {group?.currency ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Total Entitled (USD)')}>
                  {group?.totalEntitledQuantityUsd ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Total Delivered (USD)')}>
                  {group?.totalDeliveredQuantityUsd ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Total Undelivered (USD)')}>
                  {group?.totalUndeliveredQuantityUsd ?? '-'}
                </LabelizedField>
              </Grid>
            </Grid>
          </OverviewContainer>
        </ContainerColumnWithBorder>
      </Grid>
      <AcceptanceProcess
        approvalProcess={group?.approvalProcess}
        closure={
          group?.status === PaymentPlanGroupStatusEnum.CLOSED
            ? { closedBy: group.closedBy, closedDate: group.statusDate }
            : null
        }
      />
      <TableWrapper>
        <PaymentPlansTable
          filter={filter}
          canViewDetails
          title={t('Payment Plans')}
          paymentPlanGroupId={groupId}
        />
      </TableWrapper>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={group?.id} />
      )}
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanGroupDetailsPage,
  'PaymentPlanGroupDetailsPage',
);
