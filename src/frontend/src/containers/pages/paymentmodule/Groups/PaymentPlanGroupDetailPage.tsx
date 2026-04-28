import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { PageHeader } from '@core/PageHeader';
import { TableWrapper } from '@core/TableWrapper';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Grid, Typography } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

interface GroupDetail {
  id: string;
  unicefId: string;
  name: string;
  cycle: string;
}

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
  // TODO: use groupId to fetch group detail once API is available
  useParams<{ groupId: string }>();
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const [filter] = useState(initialFilter);

  // TODO: Fetch group detail from API once endpoint is available:
  // RestService.restBusinessAreasPaymentPlanGroupsRetrieve({ businessAreaSlug, id: groupId })
  const group: GroupDetail | null = null;
  const isLoading = false;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      title: t('Groups'),
      to: `/${baseUrl}/payment-module/groups`,
    },
  ];

  if (isLoading) return <LoadingComponent />;

  return (
    <>
      <PageHeader
        title={group?.name ?? t('Group Detail')}
        breadCrumbs={breadCrumbsItems}
      />
      <Grid size={{ xs: 12 }}>
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant="h6">{t('Details')}</Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Name')}>
                  {/* TODO: populated once API is ready */}
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
                  {/* TODO: link to cycle detail once API returns cycle ID */}
                  {group?.cycle ?? '-'}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Status')}>
                  {/* TODO: PaymentPlanGroup has no status field yet */}
                  -
                </LabelizedField>
              </Grid>
            </Grid>
          </OverviewContainer>
        </ContainerColumnWithBorder>
      </Grid>
      <TableWrapper>
        {/* TODO: pass paymentPlanGroup filter to PaymentPlansTable once the API supports filtering by group */}
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

export default withErrorBoundary(PaymentPlanGroupDetailPage, 'PaymentPlanGroupDetailPage');
