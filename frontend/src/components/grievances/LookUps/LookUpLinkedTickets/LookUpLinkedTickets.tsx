import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { LookUpButton } from '../../LookUpButton';
import { LookUpLinkedTicketsDisplay } from './LookUpLinkedTicketsDisplay';
import { LookUpLinkedTicketsModal } from './LookUpLinkedTicketsModal';

export const LookUpLinkedTickets = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);
  const isEditTicket = location.pathname.includes('edit-ticket');
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
          placeholder={isEditTicket}
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
