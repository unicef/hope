import { Button } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BaseSection } from '../../core/BaseSection';

interface ProgramPartnersSectionProps {
  setStep: (step: number) => void;
}

export const ProgramPartnersSection = ({
  setStep,
}: ProgramPartnersSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <BaseSection
      title={t('Programme Partners')}
      buttons={
        <Button
          onClick={() => setStep(1)}
          variant='contained'
          color='primary'
          endIcon={<AddIcon />}
        >
          {t('Add Partner')}
        </Button>
      }
    />
  );
};
