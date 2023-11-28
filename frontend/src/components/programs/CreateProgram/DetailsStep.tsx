import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramForm } from '../../../containers/forms/ProgramForm';
import { BaseSection } from '../../core/BaseSection';

interface DetailsStepProps {
  values;
  step: number;
  setStep: (step: number) => void;
}

export const DetailsStep: React.FC<DetailsStepProps> = ({
  values,
  step,
  setStep,
}) => {
  const { t } = useTranslation();
  const title = t('Details');
  const description = t(
    'To create a new Programme, please complete all required fields on the form below and save.',
  );
  return (
    <BaseSection title={title} description={description}>
      <>
        <ProgramForm values={values} />
        <Box display='flex' justifyContent='flex-end'>
          <Box mr={2}>
            <Button
              variant='outlined'
              onClick={() => setStep(step - 1)}
              disabled={step === 0}
            >
              {t('Back')}
            </Button>
          </Box>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setStep(step + 1)}
          >
            {t('Next')}
          </Button>
        </Box>
      </>
    </BaseSection>
  );
};
