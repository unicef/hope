import withErrorBoundary from '@components/core/withErrorBoundary';
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
import { RestService } from '@restgenerated/services/RestService';
import { Grid, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { PaymentPlanGroupDetailsHeader } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupDetailsHeader';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
  isFollowUp: false,
};

const PaymentPlanGroupDetailsPage = (): ReactElement => {
  const { groupId } = useParams<{ groupId: string }>();
  const { businessArea, programId, baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const [filter] = useState(initialFilter);
  const permissions = usePermissions();
  const { data: group, isLoading } = useQuery({
    queryKey: ['paymentPlanGroup', businessArea, programId, groupId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve({
        businessAreaSlug: businessArea,
        id: groupId,
        programCode: programId,
      }),
    enabled: !!groupId && !!businessArea && !!programId,
  });

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_PAYMENT_PLAN_GROUP, permissions))
    return (
      <PermissionDenied permission={PERMISSIONS.PM_VIEW_PAYMENT_PLAN_GROUP} />
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
      <TableWrapper>
        {/* TODO: filter by group once backend adds payment_plan_group to PaymentPlanFilter
            (src/hope/apps/payment/api/filters.py) and types are regenerated.
            Steps: add `payment_plan_group = UUIDFilter(field_name="payment_plan_group__id")` to
            PaymentPlanFilter, regenerate types, add optional paymentPlanGroupId prop to
            PaymentPlansTable, pass paymentPlanGroupId={groupId} here. */}
        <PaymentPlansTable
          filter={filter}
          canViewDetails
          title={t('Payment Plans')}
        />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanGroupDetailsPage,
  'PaymentPlanGroupDetailsPage',
);
