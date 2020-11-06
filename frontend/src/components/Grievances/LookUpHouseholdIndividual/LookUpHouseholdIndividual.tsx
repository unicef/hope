import React, { useState } from 'react';
import { LookUpHouseholdIndividualDisplay } from './LookUpHouseholdIndividualDisplay';
import { LookUpHouseholdIndividualModal } from './LookUpHouseholdIndividualModal';
import { LookUpButton } from '../LookUpButton';

export const LookUpHouseholdIndividual = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      {values.selectedHousehold || values.selectedIndividual ? (
        <LookUpHouseholdIndividualDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          onValueChange={onValueChange}
        />
      ) : (
        <LookUpButton
          title='Look up Household / Individual'
          handleClick={() => setLookUpDialogOpen(true)}
        />
      )}
      <LookUpHouseholdIndividualModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
