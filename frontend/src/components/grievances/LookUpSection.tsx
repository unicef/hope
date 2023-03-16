import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { GRIEVANCE_CATEGORIES } from '../../utils/constants';
import { thingForSpecificGrievanceType } from '../../utils/utils';
import { LookUpHouseholdIndividual } from './LookUps/LookUpHouseholdIndividual/LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUps/LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpLinkedTickets } from './LookUps/LookUpLinkedTickets/LookUpLinkedTickets';

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
  const renderedLookupLinkedTickets = (
    <Grid container>
      <Grid item xs={6}>
        <Box p={3}>
          <LookUpLinkedTickets values={values} onValueChange={onValueChange} />
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
      {renderedLookupLinkedTickets}
    </Grid>
  );

  const householdIndividualLinkedTicketsLookups = (
    <Grid container alignItems='center'>
      <Grid container>{renderedLookupHouseholdIndividual}</Grid>
      {renderedLookupLinkedTickets}
    </Grid>
  );
  const lookupDict = {
    [GRIEVANCE_CATEGORIES.DATA_CHANGE]: householdIndividualLinkedTicketsLookups,
    [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: allThree,
    [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: allThree,
    [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: householdIndividualLinkedTicketsLookups,
    [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: householdIndividualLinkedTicketsLookups,
    [GRIEVANCE_CATEGORIES.REFERRAL]: householdIndividualLinkedTicketsLookups,
  };
  return thingForSpecificGrievanceType(
    { category: values.category },
    lookupDict,
    renderedLookupLinkedTickets,
    {
      [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: false,
      [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: false,
      [GRIEVANCE_CATEGORIES.DATA_CHANGE]: false,
    },
  );
};
