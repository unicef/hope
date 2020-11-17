import React, { useState } from 'react';
import { LookUpButton } from '../LookUpButton';
import { LookUpPaymentRecordDisplay } from './LookUpPaymentRecordDisplay';
import { LookUpPaymentRecordModal } from './LookUpPaymentRecordModal';

export const LookUpPaymentRecord = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  const shouldDisplayPlaceholder = (): boolean => {
    return !values.selectedHousehold;
  };

  return (
    <>
      {values.selectedPaymentRecords.length ? (
        <LookUpPaymentRecordDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          onValueChange={onValueChange}
        />
      ) : (
        <LookUpButton
          placeholder={shouldDisplayPlaceholder()}
          title='Look up Payment Record'
          handleClick={() => setLookUpDialogOpen(true)}
        />
      )}
      <LookUpPaymentRecordModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
