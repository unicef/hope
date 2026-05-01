import withErrorBoundary from '@components/core/withErrorBoundary';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { TableWrapper } from '@core/TableWrapper';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Grid, Typography } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { PaymentPlanGroupDetailHeader } from './PaymentPlanGroupDetailHeader';
import { PaymentPlanGroupDetail } from './types';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
  isFollowUp: false,
};

const PaymentPlanGroupDetailPage = (): ReactElement => {
  const { groupId } = useParams<{ groupId: string }>();
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const [filter] = useState(initialFilter);

  // TODO: Fetch group detail from API once endpoint is available:
  // RestService.restBusinessAreasPaymentPlanGroupsRetrieve({ businessAreaSlug: businessArea, id: groupId })
  // Query key: ['paymentPlanGroup', businessArea, groupId]
  const group: PaymentPlanGroupDetail | null = null;
  const isLoading = false;

  if (isLoading) return <LoadingComponent />;

  return (
    <>
      <PaymentPlanGroupDetailHeader group={group} />
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
                <LabelizedField label={t('UNICEF ID')}>
                  {group?.unicefId ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Cycle')}>
                  {/* TODO: link to cycle detail once API returns cycle data */}
                  {group?.cycleName ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Status')}>
                  {/* TODO: PaymentPlanGroup status field not yet available */}
                  {group?.status ?? '-'}
                </LabelizedField>
              </Grid>
            </Grid>
          </OverviewContainer>
        </ContainerColumnWithBorder>
      </Grid>
      <TableWrapper>
        {/* TODO: Filter PaymentPlansTable by paymentPlanGroup once the API supports it.
            Currently showing all plans — pass groupId as query param when endpoint is ready. */}
        <PaymentPlansTable
          programCycle={null as any}
          filter={filter}
          canViewDetails
          title={t('Payment Plans')}
        />
      </TableWrapper>
    </>
  );
};

export default withErrorBoundary(
  PaymentPlanGroupDetailPage,
  'PaymentPlanGroupDetailPage',
);
