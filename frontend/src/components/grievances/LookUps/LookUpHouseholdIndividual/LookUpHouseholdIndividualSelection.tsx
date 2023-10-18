import { Box, FormHelperText, Grid } from '@material-ui/core';
import React, { useState } from 'react';
import { isInvalid } from '../../../../utils/utils';
import { LookUpHouseholdIndividualSelectionDetail } from './LookUpHouseholdIndividualSelectionDetail';
import { LookUpHouseholdIndividualSelectionDisplay } from './LookUpHouseholdIndividualSelectionDisplay';

export const LookUpHouseholdIndividualSelection = ({
  onValueChange,
  values,
  errors,
  touched,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: {
  onValueChange: (field: string, value, shouldValidate?: boolean) => void;
  values;
  errors?;
  touched?;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}): React.ReactElement => {
  const [selectedHousehold, setSelectedHousehold] = useState(
    values.selectedHousehold,
  );
  const [selectedIndividual, setSelectedIndividual] = useState(
    values.selectedIndividual,
  );
  return (
    <>
      <LookUpHouseholdIndividualSelectionDetail
        initialValues={values}
        onValueChange={onValueChange}
        selectedIndividual={selectedIndividual}
        selectedHousehold={selectedHousehold}
        setSelectedHousehold={setSelectedHousehold}
        setSelectedIndividual={setSelectedIndividual}
        redirectedFromRelatedTicket={redirectedFromRelatedTicket}
        isFeedbackWithHouseholdOnly={isFeedbackWithHouseholdOnly}
      />
      <Box display='flex' flexDirection='column'>
        <LookUpHouseholdIndividualSelectionDisplay
          disableUnselectHousehold={
            redirectedFromRelatedTicket || isFeedbackWithHouseholdOnly
          }
          disableUnselectIndividual={redirectedFromRelatedTicket}
          onValueChange={onValueChange}
          selectedHousehold={selectedHousehold}
          setSelectedHousehold={setSelectedHousehold}
          selectedIndividual={selectedIndividual}
          setSelectedIndividual={setSelectedIndividual}
        />
        {isInvalid('selectedIndividual', errors, touched) && (
          <Grid container spacing={4}>
            <Grid item xs={4} />
            <Grid item xs={4}>
              <FormHelperText error>
                {errors?.selectedIndividual}
              </FormHelperText>
            </Grid>
          </Grid>
        )}
        {isInvalid('selectedHousehold', errors, touched) &&
          !selectedHousehold && (
            <FormHelperText error>{errors?.selectedHousehold}</FormHelperText>
          )}
      </Box>
    </>
  );
};
