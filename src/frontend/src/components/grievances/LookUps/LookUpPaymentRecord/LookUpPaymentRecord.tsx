import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { LookUpButton } from '../../LookUpButton';
import { LookUpPaymentRecordDisplay } from './LookUpPaymentRecordDisplay';
import { LookUpPaymentRecordModal } from './LookUpPaymentRecordModal';
import { useProgramContext } from 'src/programContext';

export function LookUpPaymentRecord({
  onValueChange,
  values,
  disabled,
}: {
  onValueChange;
  values;
  disabled?;
}): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { isSocialDctType } = useProgramContext();
  const isEditTicket = location.pathname.includes('edit-ticket');
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  const shouldDisplayPlaceholder = (): boolean =>
    !values.selectedHousehold && !isSocialDctType;

  return (
    <>
      {values.selectedPaymentRecords?.length ? (
        <LookUpPaymentRecordDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          disabled={disabled}
          onValueChange={onValueChange}
        />
      ) : (
        !isEditTicket && (
          <LookUpButton
            placeholder={shouldDisplayPlaceholder()}
            title={t('Look up Payment Record')}
            handleClick={() => setLookUpDialogOpen(true)}
          />
        )
      )}
      <LookUpPaymentRecordModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
}
