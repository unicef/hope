import { DividerLine } from '@components/core/DividerLine';
import { PduSubtypeChoicesDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Button, Grid, IconButton } from '@mui/material';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

interface ProgramFieldSeriesStepProps {
  values: {
    //TODO: Define the type of pduFields
    pduFields: Array<any>;
  };
  handleNext?: () => Promise<void>;
  setStep: (step: number) => void;
  step: number;
  programHasRdi?: boolean;
  pdusubtypeChoicesData?: PduSubtypeChoicesDataQuery;
}

export const ProgramFieldSeriesStep = ({
  values,
  handleNext,
  setStep,
  step,
  programHasRdi,
  pdusubtypeChoicesData,
}: ProgramFieldSeriesStepProps) => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const handleNextClick = async (): Promise<void> => {
    if (handleNext) {
      await handleNext();
    }
  };

  const mappedPduSubtypeChoices = pdusubtypeChoicesData?.pduSubtypeChoices.map(
    (el) => ({
      value: el.value,
      name: el.displayName,
    }),
  );

  return (
    <>
      <FieldArray
        name="pduFields"
        render={(arrayHelpers) => (
          <div>
            {values.pduFields && values.pduFields.length > 0
              ? values.pduFields.map((_field, index) => (
                  <Box key={index} pt={3} pb={3}>
                    <Grid container spacing={3} alignItems="center">
                      <Grid item xs={3}>
                        <Field
                          name={`pduFields.${index}.name`}
                          fullWidth
                          variant="outlined"
                          label={t('Time Series Field Name')}
                          component={FormikTextField}
                          disabled={programHasRdi}
                        />
                      </Grid>
                      <Grid item xs={3}>
                        <Field
                          name={`pduFields.${index}.pduData.subtype`}
                          fullWidth
                          variant="outlined"
                          label={t('Data Type')}
                          component={FormikSelectField}
                          choices={mappedPduSubtypeChoices}
                          disabled={programHasRdi}
                        />
                      </Grid>
                      <Grid item xs={3}>
                        <Field
                          name={`pduFields.${index}.pduData.numberOfRounds`}
                          fullWidth
                          variant="outlined"
                          label={t('Number of Expected Rounds')}
                          component={FormikSelectField}
                          choices={[...Array(10).keys()].map((n) => ({
                            value: n + 1,
                            label: `${n + 1}`,
                          }))}
                          disabled={programHasRdi}
                        />
                      </Grid>
                      {_field.pduData.numberOfRounds &&
                        [
                          ...Array(
                            Number(_field.pduData.numberOfRounds),
                          ).keys(),
                        ].map((round) => (
                          <Grid item xs={12} key={round}>
                            <Field
                              name={`pduFields.${index}.pduData.roundsNames.${round}`}
                              fullWidth
                              variant="outlined"
                              label={`${t('Round')} ${round + 1} ${t('Name')}`}
                              component={FormikTextField}
                              disabled={programHasRdi}
                            />
                          </Grid>
                        ))}
                      {!(
                        values.pduFields.length === 1 ||
                        (!_field.fieldName &&
                          !_field.dataType &&
                          !_field.numberOfRounds)
                      ) && (
                        <Grid item xs={1}>
                          <IconButton
                            onClick={() => arrayHelpers.remove(index)}
                            disabled={programHasRdi}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Grid>
                      )}
                    </Grid>
                    {values.pduFields.length > 1 &&
                      index < values.pduFields.length - 1 && <DividerLine />}
                  </Box>
                ))
              : null}
            <Box mt={6}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() =>
                  arrayHelpers.push({
                    name: '',
                    pduData: {
                      subtype: '',
                      numberOfRounds: null,
                      roundsNames: [],
                    },
                  })
                }
                endIcon={<AddIcon />}
                disabled={programHasRdi}
                data-cy="button-add-time-series-field"
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
        <Box display="flex">
          <Box mr={2}>
            <Button
              data-cy="button-back"
              variant="outlined"
              onClick={() => setStep(step - 1)}
            >
              {t('Back')}
            </Button>
          </Box>
          <Button
            variant="contained"
            color="primary"
            data-cy="button-next"
            onClick={handleNextClick}
          >
            {t('Next')}
          </Button>
        </Box>
      </Box>
    </>
  );
};
