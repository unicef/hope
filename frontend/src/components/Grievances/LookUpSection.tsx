import { Box } from '@material-ui/core';
import React from 'react';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUpPaymentRecord';

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
        return <div>Data Change</div>;
      case '3':
        return <div>Sensitive Grievance</div>;
      case '4':
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
      case '5':
        return <div>Negative Feedback</div>;
      case '6':
        return <div>Referral</div>;
      case '7':
        return <div>Positive Feedback</div>;
      case '8':
        return <div>Deduplication</div>;

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
