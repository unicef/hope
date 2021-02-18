import React from 'react';
import styled from 'styled-components';
import { Grid } from '@material-ui/core';
import { TabPanel } from '../../components/TabPanel';
import { DashboardPaper } from '../../components/Dashboard/DashboardPaper';
import { ProgrammesBySector } from '../../components/Dashboard/charts/ProgrammesBySector';
import { PlannedBudget } from '../../components/Dashboard/charts/PlannedBudget';
import { VolumeByDeliveryMechanism } from '../../components/Dashboard/charts/VolumeByDeliveryMechanism';
import { PaymentsChart } from '../../components/Dashboard/charts/PaymentsChart';
import { GrievancesSection } from '../../components/Dashboard/sections/GrievancesSection';
import { TotalNumberOfIndividualsReachedSection } from '../../components/Dashboard/sections/TotalNumberOfIndividualsReachedSection';
import { TotalNumberOfChildrenReachedSection } from '../../components/Dashboard/sections/TotalNumberOfChildrenReachedSection';
import { TotalNumberOfHouseholdsReachedSection } from '../../components/Dashboard/sections/TotalNumberOfHouseholdsReachedSection';
import { TotalAmountTransferredSection } from '../../components/Dashboard/sections/TotalAmountTransferredSection';
import { PaymentVerificationSection } from '../../components/Dashboard/sections/PaymentVerificationSection';
import { TotalAmountPlannedAndTransferredSection } from '../../components/Dashboard/sections/TotalAmountPlannedAndTransferredSection';
import { TotalCashTransferredByAdministrativeAreaTable } from '../../components/Dashboard/TotalCashTransferredByAdministrativeAreaTable';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useAllChartsQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../../components/LoadingComponent';

const PaddingContainer = styled.div`
  padding: 20px;
`;
const PadddingLeftContainer = styled.div`
  padding-left: 20px;
`;
const CardTextLight = styled.div`
  text-transform: capitalize;
  color: #a4a4a4;
  font-weight: 500;
  font-size: 12px;
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
  const { data, loading } = useAllChartsQuery({
    variables: {
      year: parseInt(year, 10),
      businessAreaSlug: businessArea,
      program: filter.program,
      administrativeArea: filter.administrativeArea?.node?.id,
    },
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <TabPanel value={selectedTab} index={selectedTab}>
      <PaddingContainer>
        <Grid container>
          <Grid item xs={8}>
            <TotalAmountTransferredSection
              data={data.sectionTotalTransferred}
            />
            <TotalAmountPlannedAndTransferredSection
              data={data.chartTotalTransferredCashByCountry}
            />
            <DashboardPaper title='Number of Programmes by Sector'>
              <ProgrammesBySector data={data.chartProgrammesBySector} />
            </DashboardPaper>
            <DashboardPaper title='Planned Budget and Total Transferred to Date'>
              <PlannedBudget data={data.chartPlannedBudget} />
            </DashboardPaper>
            <DashboardPaper title='Total Cash Transferred  by Administrative Area'>
              <TotalCashTransferredByAdministrativeAreaTable
                data={data.tableTotalCashTransferredByAdministrativeArea?.data}
              />
            </DashboardPaper>
            <PaymentVerificationSection data={data.chartPaymentVerification} />
          </Grid>
          <Grid item xs={4}>
            <PadddingLeftContainer>
              <Grid container spacing={3}>
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
                  <DashboardPaper title='Volume by Delivery Mechanism'>
                    <CardTextLight>IN USD</CardTextLight>
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
