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
import { Box, Grid, Link, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { PaymentPlanGroupDetailsHeader } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupDetailsHeader';
import { isGroupBackgroundActionBusy } from './utils';
import { useQueryClient } from '@tanstack/react-query';

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
  const wasBusy = useRef(false);
  useEffect(() => {
    const isBusy = isGroupBackgroundActionBusy(group ?? null);
    if (wasBusy.current && !isBusy) {
      queryClient.invalidateQueries({ queryKey: ['businessAreasPaymentPlans'] });
      queryClient.invalidateQueries({ queryKey: ['businessAreasProgramsPaymentPlansList'] });
    }
    wasBusy.current = isBusy;
  }, [group, queryClient]);
  const { data: group, isLoading } = useQuery({
    queryKey: ['paymentPlanGroup', businessArea, programId, groupId],
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

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL, permissions))
    return (
      <PermissionDenied permission={PERMISSIONS.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL} />
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
      {group?.batches && group.batches.length > 0 && (
        <Grid size={{ xs: 12 }}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant="h6">{t('Batches')}</Typography>
            </Title>
            {group.batches.map((batch) => (
              <Box
                key={batch.exportTag}
                display="flex"
                alignItems="center"
                gap={2}
                py={1}
              >
                <BlackLink
                  to={`/${baseUrl}/payment-module/groups/${groupId}/batches/${encodeURIComponent(String(batch.exportTag))}`}
                >
                  {t('Batch')} #{batch.exportTag}
                </BlackLink>
                {batch.exportFileLink ? (
                  <Link
                    href={`/api/download-payment-plan-group-batch/${groupId}/${batch.exportTag}`}
                    download
                    underline="hover"
                    data-cy={`batch-download-link-${batch.exportTag}`}
                  >
                    {t('Download')}
                  </Link>
                ) : null}
              </Box>
            ))}
          </ContainerColumnWithBorder>
        </Grid>
      )}
      <TableWrapper>
        <PaymentPlansTable
          filter={filter}
          canViewDetails
          title={t('Payment Plans')}
          paymentPlanGroupId={groupId}
        />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanGroupDetailsPage,
  'PaymentPlanGroupDetailsPage',
);
