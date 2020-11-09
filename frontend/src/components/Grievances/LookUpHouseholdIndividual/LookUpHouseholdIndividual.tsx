import React, { useState } from 'react';
import { LookUpButton } from '../LookUpButton';
import { LookUpHouseholdIndividualDisplay } from './LookUpHouseholdIndividualDisplay';
import { LookUpHouseholdIndividualModal } from './LookUpHouseholdIndividualModal';

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
