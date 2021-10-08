import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { GRIEVANCE_CATEGORIES } from '../../utils/constants';
import { thingForSpecificGrievanceType } from '../../utils/utils';
import { AddDocumentation } from './AddDocumentation';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual/LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpRelatedTickets } from './LookUpRelatedTickets/LookUpRelatedTickets';

export const LookUpSection = ({
  onValueChange,
  values,
  disabledHouseholdIndividual,
  disabledPaymentRecords,
  errors,
  touched,
}: {
  onValueChange;
  values;
  disabledHouseholdIndividual?;
  disabledPaymentRecords?;
  errors?;
  touched?;
}): React.ReactElement => {
  const renderedLookupHouseholdIndividual = (
    <Grid item xs={6}>
      <Box p={3}>
        <LookUpHouseholdIndividual
          values={values}
          onValueChange={onValueChange}
          disabled={disabledHouseholdIndividual}
          errors={errors}
          touched={touched}
        />
      </Box>
    </Grid>
  );
  const renderedLookupRelatedTickets = (
    <Grid container>
      <Grid item xs={6}>
        <Box p={3}>
          <LookUpRelatedTickets values={values} onValueChange={onValueChange} />
        </Box>
      </Grid>
      <Grid item xs={6}>
        <Box p={3}>
          <AddDocumentation values={values} onValueChange={onValueChange} />
        </Box>
      </Grid>
    </Grid>
  );
  const renderedLookupPaymentRecords = (
    <Grid item xs={6}>
      <Box p={3}>
        <LookUpPaymentRecord
          disabled={disabledPaymentRecords}
          values={values}
          onValueChange={onValueChange}
        />
      </Box>
    </Grid>
  );
  const allThree = (
    <Grid container alignItems='center'>
      {renderedLookupHouseholdIndividual}
      {renderedLookupPaymentRecords}
      {renderedLookupRelatedTickets}
    </Grid>
  );

  const householdIndividualRelatedTicketsLookups = (
    <Grid container alignItems='center'>
      {renderedLookupHouseholdIndividual}
      {renderedLookupRelatedTickets}
    </Grid>
  );
  const lookupDict = {
    [GRIEVANCE_CATEGORIES.DATA_CHANGE]: householdIndividualRelatedTicketsLookups,
    [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: allThree,
    [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: allThree,
    [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: householdIndividualRelatedTicketsLookups,
    [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: householdIndividualRelatedTicketsLookups,
    [GRIEVANCE_CATEGORIES.REFERRAL]: householdIndividualRelatedTicketsLookups,
  };
  return thingForSpecificGrievanceType(
    { category: values.category },
    lookupDict,
    renderedLookupRelatedTickets,
    {
      [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: false,
      [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: false,
      [GRIEVANCE_CATEGORIES.DATA_CHANGE]: false,
    },
  );
};
