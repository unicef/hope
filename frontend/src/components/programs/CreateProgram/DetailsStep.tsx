import { Box, Button } from '@mui/material';
import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ProgramForm } from '../../../containers/forms/ProgramForm';
import { BaseSection } from '../../core/BaseSection';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

interface DetailsStepProps {
  values;
  handleNext?: () => Promise<void>;
}

export const DetailsStep: React.FC<DetailsStepProps> = ({
  values,
  handleNext,
}) => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
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
        <Box display="flex" justifyContent="space-between">
          <Button
            data-cy="button-cancel"
            component={Link}
            to={`/${baseUrl}/list`}
          >
            {t('Cancel')}
          </Button>
          <Button
            variant="contained"
            color="primary"
            data-cy="button-next"
            onClick={handleNextClick}
          >
            {t('Next')}
          </Button>
        </Box>
      </>
    </BaseSection>
  );
};
