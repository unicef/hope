import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { AllChartsQuery } from '../../../__generated__/graphql';
import { Missing } from '../../Missing';
import { PaymentVerificationChart } from '../charts/PaymentVerificationChart';
import { DashboardPaper } from '../DashboardPaper';

interface PaymentVerificationSectionProps {
  data: AllChartsQuery['chartPaymentVerification'];
}
export const PaymentVerificationSection = ({
  data,
}: PaymentVerificationSectionProps): React.ReactElement => {
  if (!data) return null;
  return (
    <DashboardPaper title='Payment Verification'>
      <Box mt={3}>
        <Typography variant='subtitle2'>
          {data.households} {data.households === 1 ? 'Household' : 'Households'}{' '}
          contacted
        </Typography>
        <Typography variant='caption'>
          12% average sampling <Missing />
        </Typography>
      </Box>
      <PaymentVerificationChart data={data} />
    </DashboardPaper>
  );
};
