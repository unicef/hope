import React, { useState } from 'react';
import { LookUpButton } from '../LookUpButton';
import { LookUpHouseholdIndividualDisplay } from './LookUpHouseholdIndividualDisplay';
import { LookUpHouseholdIndividualModal } from './LookUpHouseholdIndividualModal';

export const LookUpHouseholdIndividual = ({
  onValueChange,
  values,
  disabled
}:{
  onValueChange,
  values,
  disabled?:boolean
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      {values.selectedHousehold || values.selectedIndividual||disabled ? (
        <LookUpHouseholdIndividualDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          disabled={disabled}
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
