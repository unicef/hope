import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual/LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpRelatedTickets } from './LookUpRelatedTickets';

export const LookUpSection = ({
  category,
  onValueChange,
  values,
}): React.ReactElement => {
  const LookUpForCategory = (): React.ReactElement => {
    switch (category) {
      case '1':
        return <div>Payment Verification</div>;
      case '2':
        return (
          <Grid container alignItems='center'>
            <Grid container>
              <Grid item xs={6}>
                <Box p={3}>
                  <LookUpHouseholdIndividual
                    values={values}
                    onValueChange={onValueChange}
                  />
                </Box>
              </Grid>
            </Grid>
            <Grid container>
              <Grid item xs={6}>
                <Box p={3}>
                  <LookUpRelatedTickets />
                </Box>
              </Grid>
            </Grid>
          </Grid>
        );
      case '3':
        return (
          <Grid container alignItems='center'>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpHouseholdIndividual
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpPaymentRecord
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
            <Grid container>
              <Grid item xs={6}>
                <Box p={3}>
                  <LookUpRelatedTickets />
                </Box>
              </Grid>
            </Grid>
          </Grid>
        );
      case '4':
        return (
          <Grid container alignItems='center'>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpHouseholdIndividual
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpPaymentRecord
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
            <Grid container>
              <Grid item xs={6}>
                <Box p={3}>
                  <LookUpRelatedTickets />
                </Box>
              </Grid>
            </Grid>
          </Grid>
        );
      case '5':
        return (
          <Grid container>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpRelatedTickets />
              </Box>
            </Grid>
          </Grid>
        );
      case '6':
        return (
          <Grid container>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpRelatedTickets />
              </Box>
            </Grid>
          </Grid>
        );
      case '7':
        return (
          <Grid container>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpRelatedTickets />
              </Box>
            </Grid>
          </Grid>
        );
      case '8':
        return <div>Deduplication</div>;
      default:
        return <div>Other category of the ticket</div>;
    }
  };
  return LookUpForCategory();
};
