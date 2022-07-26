import { Grid } from '@material-ui/core';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentsChart } from '../../../components/dashboard/charts/PaymentsChart';
import { ProgrammesBySector } from '../../../components/dashboard/charts/ProgrammesBySector';
import { TotalTransferredByMonth } from '../../../components/dashboard/charts/TotalTransferredByMonth';
import { VolumeByDeliveryMechanism } from '../../../components/dashboard/charts/VolumeByDeliveryMechanism';
import { DashboardPaper } from '../../../components/dashboard/DashboardPaper';
import { GrievancesSection } from '../../../components/dashboard/sections/GrievancesSection/GrievancesSection';
import { PaymentVerificationSection } from '../../../components/dashboard/sections/PaymentVerificationSection/PaymentVerificationSection';
import { TotalAmountTransferredSectionByAdminAreaSection } from '../../../components/dashboard/sections/TotalAmountTransferredByAdminAreaSection/TotalAmountTransferredByAdminAreaSection';
import { TotalAmountTransferredSection } from '../../../components/dashboard/sections/TotalAmountTransferredSection/TotalAmountTransferredSection';
import { TotalNumberOfChildrenReachedSection } from '../../../components/dashboard/sections/TotalNumberOfChildrenReachedSection/TotalNumberOfChildrenReachedSection';
import { TotalNumberOfHouseholdsReachedSection } from '../../../components/dashboard/sections/TotalNumberOfHouseholdsReachedSection/TotalNumberOfHouseholdsReachedSection';
import { TotalNumberOfIndividualsReachedSection } from '../../../components/dashboard/sections/TotalNumberOfIndividualsReachedSection/TotalNumberOfIndividualsReachedSection';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { TabPanel } from '../../../components/core/TabPanel';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  useAllChartsQuery,
  useGlobalAreaChartsLazyQuery,
} from '../../../__generated__/graphql';
import { TotalAmountTransferredByCountrySection } from '../../../components/dashboard/sections/TotalAmountTransferredByCountrySection';

const PaddingContainer = styled.div`
  padding: 20px;
`;
const ChartWrapper = styled.div`
  height: ${(props) => (props.numberOfProgrammes <= 3 ? '200px' : '400px')};
`;
const PadddingLeftContainer = styled.div`
  padding-left: 20px;
`;
const CardTextLight = styled.div`
  text-transform: capitalize;
  color: #a4a4a4;
  font-weight: 500;
  font-size: ${(props) => (props.large ? '16px' : '12px')};
`;

interface DashboardYearPageProps {
  year: string;
  selectedTab: number;
  filter;
}
export function DashboardYearPage({
  year,
  selectedTab,
  filter,
}: DashboardYearPageProps): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const isGlobal = businessArea === 'global';

  const sharedVariables = {
    year: parseInt(year, 10),
  };

  const { data, loading } = useAllChartsQuery({
    variables: {
      ...sharedVariables,
      businessAreaSlug: businessArea,
      ...(!isGlobal && {
        program: filter.program,
        administrativeArea: filter.administrativeArea?.node?.id,
      }),
    },
    fetchPolicy: 'cache-and-network',
  });

  const [
    loadGlobal,
    { data: globalData, loading: globalLoading },
  ] = useGlobalAreaChartsLazyQuery({
    variables: sharedVariables,
  });

  useEffect(() => {
    if (isGlobal) {
      loadGlobal();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [businessArea]);

  if (isGlobal) {
    if (loading || globalLoading) return <LoadingComponent />;
    if (!data || !globalData) return null;
  } else {
    if (loading) return <LoadingComponent />;
    if (!data) return null;
  }
  return (
    <TabPanel value={selectedTab} index={selectedTab}>
      <PaddingContainer>
        <Grid container>
          <Grid item xs={8}>
            <TotalAmountTransferredSection
              data={data.sectionTotalTransferred}
            />
            <TotalAmountTransferredByCountrySection
              data={globalData?.chartTotalTransferredCashByCountry}
            />
            <DashboardPaper title={t('Number of Programmes by Sector')}>
              <ChartWrapper
                numberOfProgrammes={
                  data.chartProgrammesBySector?.labels.length || 0
                }
              >
                <ProgrammesBySector data={data.chartProgrammesBySector} />
              </ChartWrapper>
            </DashboardPaper>
            <DashboardPaper title={t('Total Transferred by Month')}>
              <TotalTransferredByMonth
                data={data.chartTotalTransferredByMonth}
              />
            </DashboardPaper>
            <TotalAmountTransferredSectionByAdminAreaSection
              year={year}
              filter={filter}
              businessArea={businessArea}
            />
            <PaymentVerificationSection data={data.chartPaymentVerification} />
          </Grid>
          <Grid item xs={4}>
            <PadddingLeftContainer>
              <Grid container spacing={6}>
                <Grid item xs={12}>
                  <TotalNumberOfHouseholdsReachedSection
                    data={data.sectionHouseholdsReached}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TotalNumberOfIndividualsReachedSection
                    data={data.sectionIndividualsReached}
                    chartDataIndividuals={
                      data.chartIndividualsReachedByAgeAndGender
                    }
                    chartDataIndividualsDisability={
                      data.chartIndividualsWithDisabilityReachedByAge
                    }
                  />
                </Grid>
                <Grid item xs={12}>
                  <TotalNumberOfChildrenReachedSection
                    data={data.sectionChildReached}
                  />
                </Grid>
                <Grid item xs={12}>
                  <DashboardPaper
                    title={t('Volume by Delivery Mechanism in USD')}
                    noMarginTop
                    extraPaddingTitle={false}
                  >
                    <CardTextLight large>
                      {t('Delivery type in CashAssist')}
                    </CardTextLight>
                    <VolumeByDeliveryMechanism
                      data={data.chartVolumeByDeliveryMechanism}
                    />
                  </DashboardPaper>
                  <GrievancesSection data={data.chartGrievances} />
                  <DashboardPaper title='Payments'>
                    <PaymentsChart data={data.chartPayment} />
                  </DashboardPaper>
                </Grid>
              </Grid>
            </PadddingLeftContainer>
          </Grid>
        </Grid>
      </PaddingContainer>
    </TabPanel>
  );
}
