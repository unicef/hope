import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LookUpButton } from '../../LookUpButton';
import { LookUpDelegateDisplay } from '@components/grievances/LookUps/LookUpDelegate/LookUpDelegateDisplay';
import { LookUpDelegateModal } from '@components/grievances/LookUps/LookUpDelegate/LookUpDelegateModal';

export function LookUpDelegate({
  onValueChange,
  values,
  disabled,
}: {
  onValueChange;
  values;
  disabled?;
}): ReactElement {
  const { t } = useTranslation();
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      {values.selectedDelegate ? (
        <LookUpDelegateDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          disabled={disabled}
          onValueChange={onValueChange}
        />
      ) : (
        <LookUpButton
          title={t('Update Delegate')}
          handleClick={() => setLookUpDialogOpen(true)}
        />
      )}
      <LookUpDelegateModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
}
