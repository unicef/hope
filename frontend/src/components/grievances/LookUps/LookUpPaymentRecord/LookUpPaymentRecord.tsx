import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LookUpButton } from '../../LookUpButton';
import { LookUpPaymentRecordDisplay } from './LookUpPaymentRecordDisplay';
import { LookUpPaymentRecordModal } from './LookUpPaymentRecordModal';

export const LookUpPaymentRecord = ({
  onValueChange,
  values,
  disabled,
  paymentModalWithRadioButtons,
}: {
  onValueChange;
  values;
  disabled?;
  paymentModalWithRadioButtons?;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  const shouldDisplayPlaceholder = (): boolean => {
    return !values.selectedHousehold;
  };

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
        <LookUpButton
          placeholder={shouldDisplayPlaceholder()}
          title={t('Look up Payment Record')}
          handleClick={() => setLookUpDialogOpen(true)}
        />
      )}
      <LookUpPaymentRecordModal
        paymentModalWithRadioButtons={paymentModalWithRadioButtons}
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
