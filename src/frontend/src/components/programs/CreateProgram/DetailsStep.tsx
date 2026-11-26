import { Box, Button, FormHelperText } from '@mui/material';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import ProgramForm from '@containers/forms/ProgramForm';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { FC } from 'react';

interface DetailsStepProps {
  values;
  handleNext?: () => Promise<void>;
  errors: any;
  programId?: string;
  programHasRdi?: boolean;
  program?: ProgramDetail;
}

export const DetailsStep: FC<DetailsStepProps> = ({
  values,
  handleNext,
  errors,
  programId: formProgramId,
  programHasRdi,
  program,
}) => {
  const { t } = useTranslation();
  const { businessArea, programId, baseUrl } = useBaseUrl();

  const handleNextClick = async (): Promise<void> => {
    if (handleNext) {
      await handleNext();
    }
  };

  return (
    <>
      <ProgramForm
        values={values}
        programHasRdi={programHasRdi}
        errors={errors}
        program={program}
      />
      {errors?.documentationToUpdate && (
        <FormHelperText error>{errors.documentationToUpdate}</FormHelperText>
      )}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <Button
          data-cy="button-cancel"
          component={Link}
          to={
            formProgramId
              ? `/${businessArea}/programs/${programId}/details/${formProgramId}`
              : `/${baseUrl}/list`
          }
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
