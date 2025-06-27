import { Box, FormHelperText, Grid2 as Grid } from '@mui/material';
import { ReactElement, useEffect, useState } from 'react';
import { isInvalid } from '@utils/utils';
import { LookUpHouseholdIndividualSelectionDetail } from './LookUpHouseholdIndividualSelectionDetail';
import { LookUpHouseholdIndividualSelectionDisplay } from './LookUpHouseholdIndividualSelectionDisplay';
import { useProgramContext } from 'src/programContext';

export function LookUpHouseholdIndividualSelection({
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
}): ReactElement {
  const { isSocialDctType } = useProgramContext();
  const [selectedHousehold, setSelectedHousehold] = useState(
    values.selectedHousehold,
  );
  const [selectedIndividual, setSelectedIndividual] = useState(
    values.selectedIndividual,
  );

  useEffect(() => {
    if (selectedHousehold?.admin2) {
      onValueChange('admin', selectedHousehold.admin2.id);
      onValueChange('admin2', selectedHousehold.admin2.id);
    } else {
      onValueChange('admin', null);
      onValueChange('admin2', null);
    }
  }, [selectedHousehold, onValueChange]);

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
      <Box display="flex" flexDirection="column">
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
            {!isSocialDctType && <Grid size={{ xs:4 }} />}
            <Grid size={{ xs: 4 }}>
              {!selectedIndividual && (
                <FormHelperText error>
                  {errors?.selectedIndividual}
                </FormHelperText>
              )}
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
}
