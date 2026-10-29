import withErrorBoundary from '@components/core/withErrorBoundary';
import AcceptanceProcess from '@components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { ConversionToUsd } from '@components/paymentmodule/PaymentPlanDetails/ConversionToUsd';
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
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
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
import FundsCommitmentSection from '@components/paymentmodule/PaymentPlanGroupDetails/FundsCommitment/FundsCommitmentSection';
import { VisionStatusSection } from '@components/paymentmodule/PaymentPlanGroupDetails/VisionStatusSection';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { ExportGroupSummaryPdfButton } from './actions/ExportGroupSummaryPdfButton';
import { LinkedGroupsTable } from './LinkedGroupsTable';
import type { PaymentPlanGroupDetail } from './types';
import { isGroupBackgroundActionBusy, planTypeDisplayLabel } from './utils';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

const isVisionReviewActive = (group: PaymentPlanGroupDetail | null): boolean =>
  group !== null &&
  group.status === PaymentPlanGroupStatusEnum.IN_REVIEW &&
  'visionManaged' in group &&
  group.visionManaged === true;

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
    refetchInterval: (query) => {
      const currentGroup = query.state.data ?? null;
      if (isGroupBackgroundActionBusy(currentGroup)) return 3000;
      return isVisionReviewActive(currentGroup) ? 60000 : false;
    },
    refetchIntervalInBackground: true,
  });

  const wasBusy = useRef(false);
  const wasVisionReviewActive = useRef(false);
  useEffect(() => {
    const isBusy = isGroupBackgroundActionBusy(group ?? null);
    const visionReviewActive = isVisionReviewActive(group ?? null);
    if (
      (wasBusy.current && !isBusy) ||
      (wasVisionReviewActive.current && !visionReviewActive)
    ) {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
      });
    }
    wasBusy.current = isBusy;
    wasVisionReviewActive.current = visionReviewActive;
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
              {group?.planType && group.planType !== PlanTypeEnum.REGULAR && (
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('Type')}>
                    {t(planTypeDisplayLabel(group.planType))}
                  </LabelizedField>
                </Grid>
              )}
              {group?.sourceGroup && (
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('Created from')}>
                    <BlackLink
                      to={`/${baseUrl}/payment-module/groups/${group.sourceGroup.id}`}
                      data-cy="source-group-link"
                    >
                      {group.sourceGroup.unicefId ?? group.sourceGroup.name}
                    </BlackLink>
                  </LabelizedField>
                </Grid>
              )}
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
                <LabelizedField label={t('Dispersion Start Date')}>
                  {group?.dispersionStartDate ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Dispersion End Date')}>
                  {group?.dispersionEndDate ?? '-'}
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
        headerAction={<ExportGroupSummaryPdfButton group={group ?? null} />}
      />
      {group && (
        <ConversionToUsd
          owner={group}
          ownerType="group"
          permissions={permissions}
        />
      )}
      {group && <VisionStatusSection group={group} />}
      {group &&
        [
          PaymentPlanGroupStatusEnum.IN_REVIEW,
          PaymentPlanGroupStatusEnum.ACCEPTED,
          PaymentPlanGroupStatusEnum.FINISHED,
        ].includes(group.status) && (
          <FundsCommitmentSection group={group} programCode={programId} />
        )}
      {group?.linkedGroups && (
        <LinkedGroupsTable linkedGroups={group.linkedGroups} />
      )}
      <TableWrapper>
        <PaymentPlansTable
          filter={filter}
          canViewDetails
          title={t('Payment Plan Components')}
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
