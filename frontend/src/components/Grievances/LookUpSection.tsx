import { Grid } from '@material-ui/core';
import React from 'react';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual';

export const LookUpSection = ({ category }): React.ReactElement => {
  const LookUpForCategory = () => {
    switch (category) {
      case 'Positive Feedback':
        return (
          <Grid container spacing={3}>
            <Grid item xs={6}>
              <LookUpHouseholdIndividual />
            </Grid>
          </Grid>
        );
      case 'Negative Feedback':
        return <div>Negative Feedback</div>;
      case 'Grievance Complaint':
        return <div>Grievance Complaint</div>;
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
