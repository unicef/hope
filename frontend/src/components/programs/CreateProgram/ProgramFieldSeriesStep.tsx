import { Grid, Button, Box, IconButton } from '@mui/material';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { DividerLine } from '@components/core/DividerLine';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface ProgramFieldSeriesStepProps {
  values: {
    timeSeriesFields: Array<{
      fieldName: string;
      dataType: string;
      numberOfExpectedRounds: string | number;
    }>;
  };
  handleNext?: () => Promise<void>;
}

export const ProgramFieldSeriesStep = ({
  values,
  handleNext,
}: ProgramFieldSeriesStepProps) => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const handleNextClick = async (): Promise<void> => {
    if (handleNext) {
      await handleNext();
    }
  };

  return (
    <>
      <FieldArray
        name="timeSeriesFields"
        render={(arrayHelpers) => (
          <div>
            {values.timeSeriesFields && values.timeSeriesFields.length > 0
              ? values.timeSeriesFields.map((_field, index) => (
                  <Box key={index} pt={3} pb={3}>
                    <Grid container spacing={3} alignItems="center">
                      <Grid item xs={3}>
                        <Field
                          name={`timeSeriesFields.${index}.fieldName`}
                          fullWidth
                          variant="outlined"
                          label={t('Time Series Field Name')}
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={3}>
                        <Field
                          name={`timeSeriesFields.${index}.dataType`}
                          fullWidth
                          variant="outlined"
                          label={t('Data Type')}
                          component={FormikSelectField}
                          choices={[
                            { value: 'number', label: t('Number') },
                            { value: 'text', label: t('Text') },
                          ]}
                        />
                      </Grid>
                      <Grid item xs={3}>
                        <Field
                          name={`timeSeriesFields.${index}.numberOfExpectedRounds`}
                          fullWidth
                          variant="outlined"
                          label={t('Number of Expected Rounds')}
                          component={FormikSelectField}
                          choices={[...Array(10).keys()].map((n) => ({
                            value: n + 1,
                            label: `${n + 1}`,
                          }))}
                        />
                      </Grid>
                      {!(
                        values.timeSeriesFields.length === 1 ||
                        (!_field.fieldName &&
                          !_field.dataType &&
                          !_field.numberOfExpectedRounds)
                      ) && (
                        <Grid item xs={1}>
                          <IconButton
                            onClick={() => arrayHelpers.remove(index)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Grid>
                      )}
                    </Grid>
                    {values.timeSeriesFields.length > 1 &&
                      index < values.timeSeriesFields.length - 1 && (
                        <DividerLine />
                      )}
                  </Box>
                ))
              : null}
            <Box mt={6}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() =>
                  arrayHelpers.push({
                    fieldName: '',
                    dataType: '',
                    numberOfExpectedRounds: '',
                  })
                }
                endIcon={<AddIcon />}
              >
                {t('Add Time Series Fields')}
              </Button>
            </Box>
          </div>
        )}
      />
      <Box mt={3} display="flex" justifyContent="space-between">
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
  );
};
