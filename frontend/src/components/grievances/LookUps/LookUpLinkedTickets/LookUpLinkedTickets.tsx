import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LookUpButton } from '../../LookUpButton';
import { LookUpLinkedTicketsDisplay } from './LookUpLinkedTicketsDisplay';
import { LookUpLinkedTicketsModal } from './LookUpLinkedTicketsModal';

export const LookUpLinkedTickets = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const { t } = useTranslation();
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      {values.selectedLinkedTickets.length ? (
        <LookUpLinkedTicketsDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          onValueChange={onValueChange}
        />
      ) : (
        <LookUpButton
          title={t('Look up Linked Ticket')}
          handleClick={() => setLookUpDialogOpen(true)}
        />
      )}
      <LookUpLinkedTicketsModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
