import { useConfirmation } from '@components/core/ConfirmationDialog';
import { DividerLine } from '@components/core/DividerLine';
import { PduSubtypeChoicesDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Button, FormControl, Grid2 as Grid, IconButton } from '@mui/material';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

interface ProgramFieldSeriesStepProps {
  values: {
    pduFields: Array<any>;
    editMode: boolean;
  };
  handleNext?: () => Promise<void>;
  setStep: (step: number) => void;
  step: number;
  programHasRdi?: boolean;
  programHasTp?: boolean;
  pdusubtypeChoicesData?: PduSubtypeChoicesDataQuery;
  errors: any;
  programId?: string;
  setFieldValue;
  program?;
}

export const ProgramFieldSeriesStep = ({
  values,
  handleNext,
  setStep,
  step,
  programHasRdi,
  programHasTp,
  pdusubtypeChoicesData,
  errors,
  programId: formProgramId,
  setFieldValue,
  program,
}: ProgramFieldSeriesStepProps) => {
  const { t } = useTranslation();
  const { businessArea, programId, baseUrl } = useBaseUrl();

  const confirm = useConfirmation();

  const mappedPduSubtypeChoices = pdusubtypeChoicesData?.pduSubtypeChoices.map(
    (el) => ({
      value: el.value,
      name: el.displayName,
    }),
  );

  const confirmationModalTitle = t('Deleting Time Series Field');
  const confirmationText = t(
    'Are you sure you want to delete this field? This action cannot be reversed.',
  );

  const fieldDisabled = programHasRdi || programHasTp;

  return (
    <>
      <FieldArray
        name="pduFields"
        render={(arrayHelpers) => (
          <div>
            {values.pduFields && values.pduFields.length > 0
              ? values.pduFields.map((_field, index) => {
                  return (
                    <Box key={index} pt={3} pb={3}>
                      <Grid container spacing={3} alignItems="flex-start">
                        <Grid size={{ xs: 3 }}>
                          <Field
                            name={`pduFields.${index}.label`}
                            required
                            fullWidth
                            variant="outlined"
                            label={t('Time Series Field Name')}
                            component={FormikTextField}
                            disabled={fieldDisabled}
                          />
                        </Grid>
                        <Grid size={{ xs: 3 }}>
                          <Field
                            name={`pduFields.${index}.pduData.subtype`}
                            required
                            fullWidth
                            variant="outlined"
                            label={t('Data Type')}
                            component={FormikSelectField}
                            choices={mappedPduSubtypeChoices}
                            disabled={fieldDisabled}
                          />
                        </Grid>
                        <Grid size={{ xs: 3 }}>
                          <Field
                            key={values.pduFields[index].pduData.numberOfRounds}
                            name={`pduFields.${index}.pduData.numberOfRounds`}
                            fullWidth
                            required
                            variant="outlined"
                            label={t('Number of Expected Rounds')}
                            onChange={(e) => {
                              const numberOfRounds = parseInt(
                                e.target.value,
                                10,
                              );
                              const updatedRoundsNames = [
                                ...values.pduFields[index].pduData.roundsNames,
                              ];

                              if (updatedRoundsNames.length < numberOfRounds) {
                                for (
                                  let i = updatedRoundsNames.length;
                                  i < numberOfRounds;
                                  i++
                                ) {
                                  updatedRoundsNames.push('');
                                }
                              } else if (
                                updatedRoundsNames.length > numberOfRounds
                              ) {
                                updatedRoundsNames.length = numberOfRounds;
                              }

                              setFieldValue(
                                `pduFields.${index}.pduData.numberOfRounds`,
                                numberOfRounds,
                              );
                              setFieldValue(
                                `pduFields.${index}.pduData.roundsNames`,
                                updatedRoundsNames,
                              );
                            }}
                            component={FormikSelectField}
                            choices={[...Array(20).keys()].map((n) => {
                              const isDisabled =
                                values.editMode &&
                                fieldDisabled &&
                                n + 2 <=
                                  (program?.pduFields[index]?.pduData
                                    ?.numberOfRounds || 0);

                              return {
                                value: n + 1,
                                label: `${n + 1}`,
                                disabled: isDisabled,
                              };
                            })}
                          />
                        </Grid>
                        <Grid size={{ xs:1 }}>
                          <IconButton
                            onClick={() =>
                              confirm({
                                title: confirmationModalTitle,
                                content: confirmationText,
                                type: 'error',
                              }).then(() => arrayHelpers.remove(index))
                            }
                            disabled={fieldDisabled}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Grid>
                        {_field.pduData.numberOfRounds &&
                          [
                            ...Array(
                              Number(_field.pduData.numberOfRounds),
                            ).keys(),
                          ].map((round) => {
                            const selectedNumberOfRounds =
                              program?.pduFields?.[index]?.pduData
                                ?.numberOfRounds || 0;
                            const isDisabled =
                              fieldDisabled &&
                              values.editMode &&
                              round + 1 <= selectedNumberOfRounds;
                            return (
                              <Grid size={{ xs:12 }} key={round}>
                                <FormControl fullWidth variant="outlined">
                                  <Field
                                    name={`pduFields.${index}.pduData.roundsNames.${round}`}
                                    fullWidth
                                    variant="outlined"
                                    label={`${t('Round')} ${round + 1} ${t('Name')}`}
                                    component={FormikTextField}
                                    type="text"
                                    disabled={isDisabled}
                                  />
                                </FormControl>
                              </Grid>
                            );
                          })}
                      </Grid>
                      {values.pduFields.length > 1 &&
                        index < values.pduFields.length - 1 && <DividerLine />}
                    </Box>
                  );
                })
              : null}
            <Box mt={6}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() =>
                  arrayHelpers.push({
                    label: '',
                    pduData: {
                      subtype: '',
                      numberOfRounds: null,
                      roundsNames: [],
                    },
                  })
                }
                endIcon={<AddIcon />}
                disabled={fieldDisabled}
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
          to={
            formProgramId
              ? `/${businessArea}/programs/${programId}/details/${formProgramId}`
              : `/${baseUrl}/list`
          }
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
            onClick={handleNext}
            disabled={errors.pduFields && errors.pduFields.length > 0}
          >
            {t('Next')}
          </Button>
        </Box>
      </Box>
    </>
  );
};
