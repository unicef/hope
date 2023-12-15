import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramForm } from '../../../containers/forms/ProgramForm';
import { BaseSection } from '../../core/BaseSection';

interface DetailsStepProps {
  values;
  step: number;
  setStep: (step: number) => void;
  handleNext?: () => Promise<void>;
}

export const DetailsStep: React.FC<DetailsStepProps> = ({
  values,
  step,
  setStep,
  handleNext,
}) => {
  const { t } = useTranslation();
  const title = t('Details');
  const description = t(
    'To create a new Programme, please complete all required fields on the form below and save.',
  );

  const handleNextClick = async (): Promise<void> => {
    if (handleNext) {
      await handleNext();
    }
  };

  return (
    <BaseSection title={title} description={description}>
      <>
        <ProgramForm values={values} />
        <Box display='flex' justifyContent='flex-end'>
          <Button
            variant='contained'
            color='primary'
            data-cy='button-next'
            onClick={handleNextClick}
          >
            {t('Next')}
          </Button>
        </Box>
      </>
    </BaseSection>
  );
};
