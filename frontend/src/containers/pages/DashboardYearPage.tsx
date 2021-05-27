import React, {useEffect} from 'react';
import styled from 'styled-components';
import {Grid} from '@material-ui/core';
import {TabPanel} from '../../components/TabPanel';
import {DashboardPaper} from '../../components/Dashboard/DashboardPaper';
import {ProgrammesBySector} from '../../components/Dashboard/charts/ProgrammesBySector';
import {TotalTransferredByMonth} from '../../components/Dashboard/charts/TotalTransferredByMonth';
import {VolumeByDeliveryMechanism} from '../../components/Dashboard/charts/VolumeByDeliveryMechanism';
import {PaymentsChart} from '../../components/Dashboard/charts/PaymentsChart';
import {GrievancesSection} from '../../components/Dashboard/sections/GrievancesSection';
import {TotalNumberOfIndividualsReachedSection} from '../../components/Dashboard/sections/TotalNumberOfIndividualsReachedSection';
import {TotalNumberOfChildrenReachedSection} from '../../components/Dashboard/sections/TotalNumberOfChildrenReachedSection';
import {TotalNumberOfHouseholdsReachedSection} from '../../components/Dashboard/sections/TotalNumberOfHouseholdsReachedSection';
import {TotalAmountTransferredSection} from '../../components/Dashboard/sections/TotalAmountTransferredSection';
import {PaymentVerificationSection} from '../../components/Dashboard/sections/PaymentVerificationSection';
import {TotalAmountTransferredSectionByCountry} from '../../components/Dashboard/sections/TotalAmountTransferredByCountrySection';
import {useBusinessArea} from '../../hooks/useBusinessArea';
import {useAllChartsQuery, useGlobalAreaChartsLazyQuery,} from '../../__generated__/graphql';
import {LoadingComponent} from '../../components/LoadingComponent';
import {TotalAmountTransferredSectionByAdminAreaSection} from '../../components/Dashboard/sections/TotalAmountTransferredByAdminAreaSection';

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
            <TotalAmountTransferredSectionByCountry
              data={globalData?.chartTotalTransferredCashByCountry}
            />
            <DashboardPaper title='Number of Programmes by Sector'>
              <ChartWrapper
                numberOfProgrammes={data.chartProgrammesBySector.labels.length}
              >
                <ProgrammesBySector data={data.chartProgrammesBySector} />
              </ChartWrapper>
            </DashboardPaper>
            <DashboardPaper title='Total Transferred by Month'>
              <TotalTransferredByMonth
                data={data.chartTotalTransferredByMonth}
              />
            </DashboardPaper>
            <TotalAmountTransferredSectionByAdminAreaSection
              year={year}
              filter={filter}
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
                    title='Volume by Delivery Mechanism in USD'
                    noMarginTop
                    extraPaddingTitle={false}
                  >
                    <CardTextLight large>
                      Delivery type in CashAssist
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
