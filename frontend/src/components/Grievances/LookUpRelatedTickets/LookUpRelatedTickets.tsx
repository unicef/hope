import React, { useState } from 'react';
import { LookUpButton } from '../LookUpButton';
import { LookUpRelatedTicketsDisplay } from './LookUpRelatedTicketsDisplay';
import { LookUpRelatedTicketsModal } from './LookUpRelatedTicketsModal';

export const LookUpRelatedTickets = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      {values.selectedRelatedTickets.length ? (
        <LookUpRelatedTicketsDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          onValueChange={onValueChange}
        />
      ) : (
        <LookUpButton
          title='Look up Related Ticket'
          handleClick={() => setLookUpDialogOpen(true)}
        />
      )}
      <LookUpRelatedTicketsModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
