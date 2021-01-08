import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { Missing } from '../../Missing';
import { PaymentVerificationChart } from '../charts/PaymentVerificationChart';
import { DashboardPaper } from '../DashboardPaper';

export const PaymentVerificationSection = (): React.ReactElement => {
  return (
    <DashboardPaper title='Payment Verification'>
      <Box mt={3}>
        <Typography variant='subtitle2'>
          76520 Households contacted <Missing />
        </Typography>
        <Typography variant='caption'>
          12% average sampling <Missing />
        </Typography>
      </Box>
      <PaymentVerificationChart />
    </DashboardPaper>
  );
};
