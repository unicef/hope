import { Box, Button } from '@mui/material';
import * as React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ProgramForm } from '@containers/forms/ProgramForm';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface DetailsStepProps {
  values;
  handleNext?: () => Promise<void>;
  errors: any;
}

export const DetailsStep: React.FC<DetailsStepProps> = ({
  values,
  handleNext,
  errors,
}) => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const handleNextClick = async (): Promise<void> => {
    if (handleNext) {
      await handleNext();
    }
  };

  return (
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
          disabled={
            Boolean(errors) &&
            (Array.isArray(errors)
              ? errors.length > 0
              : Object.keys(errors).length > 0)
          }
        >
          {t('Next')}
        </Button>
      </Box>
    </>
  );
};
