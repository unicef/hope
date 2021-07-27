import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LookUpButton } from '../LookUpButton';
import { LookUpRelatedTicketsDisplay } from './LookUpRelatedTicketsDisplay';
import { LookUpRelatedTicketsModal } from './LookUpRelatedTicketsModal';

export const LookUpRelatedTickets = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const { t } = useTranslation();
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
          title={t('Look up Related Ticket')}
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
