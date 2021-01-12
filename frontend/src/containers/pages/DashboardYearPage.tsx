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
  // year: string;
  selectedTab: number;
}
export function DashboardYearPage({
  // year,
  selectedTab,
}: DashboardYearPageProps): React.ReactElement {
  return (
    <TabPanel value={selectedTab} index={selectedTab}>
      <PaddingContainer>
        <Grid container>
          <Grid item xs={8}>
            <TotalAmountTransferredSection />
            <TotalAmountPlannedAndTransferredSection />
            <DashboardPaper title='Number of Programmes by Sector'>
              <ProgrammesBySector />
            </DashboardPaper>
            <DashboardPaper title='Planned Budget and Total Transferred to Date'>
              <PlannedBudget />
            </DashboardPaper>
            <DashboardPaper title='Total Cash Transferred  by Administrative Area'>
              <TotalCashTransferredByAdministrativeAreaTable />
            </DashboardPaper>
            <PaymentVerificationSection />
          </Grid>
          <Grid item xs={4}>
            <PadddingLeftContainer>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TotalNumberOfHouseholdsReachedSection />
                </Grid>
                <Grid item xs={12}>
                  <TotalNumberOfIndividualsReachedSection />
                </Grid>
                <Grid item xs={12}>
                  <TotalNumberOfChildrenReachedSection />
                </Grid>
                <Grid item xs={12}>
                  <DashboardPaper title='Volume by Delivery Mechanism'>
                    <CardTextLight>IN USD</CardTextLight>
                    <VolumeByDeliveryMechanism />
                  </DashboardPaper>
                  <GrievancesSection />
                  <DashboardPaper title='Payments'>
                    <PaymentsChart />
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
