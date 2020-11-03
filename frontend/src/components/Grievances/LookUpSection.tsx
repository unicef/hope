import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUpPaymentRecord';

export const LookUpSection = ({
  category,
  onValueChange,
  values,
}): React.ReactElement => {
  const LookUpForCategory = () => {
    switch (category) {
      case 'Positive Feedback':
        return (
          <Grid container spacing={3}>
            <Grid item xs={6}>
              <LookUpHouseholdIndividual
                values={values}
                onValueChange={onValueChange}
              />
            </Grid>
          </Grid>
        );
      case 'Negative Feedback':
        return <div>Negative Feedback</div>;
      case 'Grievance Complaint':
        return (
          <Box display='flex' alignItems='center'>
            <Box p={3}>
              <LookUpHouseholdIndividual
                values={values}
                onValueChange={onValueChange}
              />
            </Box>
            <Box p={3}>
              <LookUpPaymentRecord />
            </Box>
          </Box>
        );
      case 'Payment Verification Issue':
        return <div>Payment Verification Issue</div>;
      case 'Referral':
        return <div>Referral</div>;
      case 'Data Change':
        return <div>Data Change</div>;
      case 'Sensitive Grievance ':
        return <div>Sensitive Griecance</div>;
      default:
        return <div>Some other</div>;
    }
  };
  return LookUpForCategory();
};
