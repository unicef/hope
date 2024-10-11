import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { LookUpButton } from '../../LookUpButton';
import { LookUpLinkedTicketsDisplay } from './LookUpLinkedTicketsDisplay';
import { LookUpLinkedTicketsModal } from './LookUpLinkedTicketsModal';

export function LookUpLinkedTickets({
  onValueChange,
  values,
  disabled,
}: {
  onValueChange;
  values;
  disabled?;
}): React.ReactElement {
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
          disabled={disabled}
          onValueChange={onValueChange}
        />
      ) : (
        !isEditTicket && (
          <LookUpButton
            title={t('Look up Linked Ticket')}
            handleClick={() => setLookUpDialogOpen(true)}
          />
        )
      )}
      <LookUpLinkedTicketsModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
}
