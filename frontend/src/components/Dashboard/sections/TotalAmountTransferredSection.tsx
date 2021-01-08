import { Grid } from '@material-ui/core';
import React from 'react';
import AccountBalanceWalletIcon from '@material-ui/icons/AccountBalanceWallet';
import {
  CardAmount,
  CardTextLight,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';

export const TotalAmountTransferredSection = (): React.ReactElement => {
  return (
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
  );
};
