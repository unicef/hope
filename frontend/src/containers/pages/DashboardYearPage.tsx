import React from 'react';
import styled from 'styled-components';
import { Grid } from '@material-ui/core';
import AccountBalanceWalletIcon from '@material-ui/icons/AccountBalanceWallet';
import PeopleIcon from '@material-ui/icons/People';
import PersonIcon from '@material-ui/icons/Person';
import ChildCareIcon from '@material-ui/icons/ChildCare';
import { TabPanel } from '../../components/TabPanel';
import { DashboardCard } from '../../components/Dashboard/DashboardCard';
import { DashboardPaper } from '../../components/Dashboard/DashboardPaper';

const PaddingContainer = styled.div`
  padding: 20px;
`;
const PadddingLeftContainer = styled.div`
  padding-left: 20px;
`;
const CardTitle = styled.div`
  text-transform: capitalize;
  color: #6f6f6f;
  font-weight: 500;
  font-size: 12px;
`;
const CardTextLight = styled.div`
  text-transform: capitalize;
  color: #a4a4a4;
  font-weight: 500;
  font-size: 12px;
`;
const CardAmount = styled.div`
  text-transform: capitalize;
  color: rgba(0, 0, 0, 0.87);
  font-weight: 600;
  font-size: 24px;
`;
const CardAmountSmaller = styled.div`
  text-transform: capitalize;
  color: rgba(0, 0, 0, 0.87);
  font-weight: 600;
  font-size: 20px;
`;
const IconContainer = styled.div`
  height: 40px;
  width: 40px;
  padding: 8px;
  border-radius: 3px;
  background-color: ${({ bg }) => bg};
  color: ${({ color }) => color};
  font-size: 24px;
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
            <DashboardCard color='#1E877D'>
              <Grid container justify='space-between' alignItems='center'>
                <Grid item>
                  <CardTitle>TOTAL AMOUNT TRANSFERRED</CardTitle>
                  <CardTextLight>IN USD</CardTextLight>
                </Grid>
                <Grid item>
                  <Grid container spacing={3} alignItems='center'>
                    <Grid item>
                      <CardAmount>$32634245</CardAmount>
                    </Grid>
                    <Grid item>
                      <IconContainer bg='#d9eceb' color='#03867b'>
                        <AccountBalanceWalletIcon fontSize='inherit' />
                      </IconContainer>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </DashboardCard>
            <DashboardPaper title='Number of Programmes by Sector'>
              <div>chart</div>
            </DashboardPaper>
            <DashboardPaper title='Planned Budget and Total Transferred to Date'>
              <div>chart</div>
            </DashboardPaper>
            <DashboardPaper title='Total Cash Transferred  by Administrative Area'>
              <div>chart</div>
            </DashboardPaper>
            <DashboardPaper title='Payment Verification'>
              <div>chart</div>
            </DashboardPaper>
          </Grid>
          <Grid item xs={4}>
            <PadddingLeftContainer>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <DashboardCard color='#00A9FB'>
                    <CardTitle>TOTAL NUMBER OF HOUSEHOLDS REACHED</CardTitle>
                    <Grid container justify='space-between' alignItems='center'>
                      <Grid item>
                        <CardAmountSmaller>32634245</CardAmountSmaller>
                      </Grid>
                      <Grid item>
                        <IconContainer bg='#DAF1FF' color='#00A9FB'>
                          <PeopleIcon fontSize='inherit' />
                        </IconContainer>
                      </Grid>
                    </Grid>
                  </DashboardCard>
                </Grid>
                <Grid item xs={12}>
                  <DashboardCard color='#345DA0'>
                    <CardTitle>TOTAL NUMBER OF INDIVIDUALS REACHED</CardTitle>
                    <Grid container justify='space-between' alignItems='center'>
                      <Grid item>
                        <CardAmountSmaller>169178378</CardAmountSmaller>
                      </Grid>
                      <Grid item>
                        <IconContainer bg='#D9E2EF' color='#023F90'>
                          <PersonIcon fontSize='inherit' />
                        </IconContainer>
                      </Grid>
                    </Grid>
                  </DashboardCard>
                </Grid>
                <Grid item xs={12}>
                  <DashboardCard color='#4CD0E0'>
                    <CardTitle>TOTAL NUMBER OF CHILDREN REACHED</CardTitle>
                    <Grid container justify='space-between' alignItems='center'>
                      <Grid item>
                        <CardAmountSmaller>85234657</CardAmountSmaller>
                      </Grid>
                      <Grid item>
                        <IconContainer bg='#E4F7FA' color='#4CD0E0'>
                          <ChildCareIcon fontSize='inherit' />
                        </IconContainer>
                      </Grid>
                    </Grid>
                  </DashboardCard>
                  <DashboardPaper title='Volume by Delivery Mechanism'>
                    <div>chart</div>
                  </DashboardPaper>
                  <DashboardPaper title='Grievances'>
                    <div>chart</div>
                  </DashboardPaper>
                  <DashboardPaper title='Payments'>
                    <div>chart</div>
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
