import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { GRIEVANCE_CATEGORIES } from '../../utils/constants';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual/LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpRelatedTickets } from './LookUpRelatedTickets/LookUpRelatedTickets';

export const LookUpSection = ({
  category,
  onValueChange,
  values,
}): React.ReactElement => {
  const LookUpForCategory = (): React.ReactElement => {
    switch (category) {
      case GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION:
        return <div>Payment Verification</div>;
      case GRIEVANCE_CATEGORIES.DATA_CHANGE:
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
                  <LookUpRelatedTickets
                    values={values}
                    onValueChange={onValueChange}
                  />
                </Box>
              </Grid>
            </Grid>
          </Grid>
        );
      case GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE:
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
                  <LookUpRelatedTickets
                    values={values}
                    onValueChange={onValueChange}
                  />
                </Box>
              </Grid>
            </Grid>
          </Grid>
        );
      case GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT:
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
                  <LookUpRelatedTickets
                    values={values}
                    onValueChange={onValueChange}
                  />
                </Box>
              </Grid>
            </Grid>
          </Grid>
        );
      case GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK:
        return (
          <Grid container>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpRelatedTickets
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
          </Grid>
        );
      case GRIEVANCE_CATEGORIES.REFERRAL:
        return (
          <Grid container>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpRelatedTickets
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
          </Grid>
        );
      case GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK:
        return (
          <Grid container>
            <Grid item xs={6}>
              <Box p={3}>
                <LookUpRelatedTickets
                  values={values}
                  onValueChange={onValueChange}
                />
              </Box>
            </Grid>
          </Grid>
        );
      case GRIEVANCE_CATEGORIES.DEDUPLICATION:
        return <div>Deduplication</div>;
      default:
        return <div />;
    }
  };
  return LookUpForCategory();
};
