import { Button, DialogContent, DialogTitle, Grid } from '@mui/material';
import { Field, Formik } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useCopyTargetPopulationMutation } from '@generated/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate } from 'react-router-dom';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
  programCycleId: Yup.object().shape({
    value: Yup.string().required('Program Cycle is required'),
  }),
});

interface DuplicateTargetPopulationProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  targetPopulationId: string;
}

export const DuplicateTargetPopulation = ({
  open,
  setOpen,
  targetPopulationId,
}: DuplicateTargetPopulationProps): React.ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [mutate, { loading }] = useCopyTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const initialValues = {
    name: '',
    id: targetPopulationId,
    programCycleId: {
      value: '',
      name: '',
    },
  };

  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <Formik
        validationSchema={validationSchema}
        initialValues={initialValues}
        onSubmit={async (values) => {
          try {
            const programCycleId = values.programCycleId.value;
            const res = await mutate({
              variables: {
                input: { targetPopulationData: { ...values, programCycleId } },
              },
            });
            setOpen(false);
            showMessage(t('Target Population Duplicated'));
            navigate(
              `/${baseUrl}/target-population/${res.data.copyTargetPopulation.targetPopulation.id}`,
            );
          } catch (e) {
            e.graphQLErrors.map((x) => showMessage(x.message));
          }
        }}
      >
        {({ submitForm, setFieldValue, values, errors }) => (
          <>
            {open && <AutoSubmitFormOnEnter />}
            <DialogTitleWrapper>
              <DialogTitle>Duplicate Target Population?</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                {t(
                  'Please use a unique name for the copy of this Target Population.',
                )}
                <br /> <strong>{t('Note')}</strong>:{' '}
                {t(
                  'This duplicate will copy the Target Criteria of the Programme Population and update to the latest results from the system.',
                )}
              </DialogDescription>
              <Grid container spacing={4}>
                <Grid item xs={12}>
                  <Field
                    name="name"
                    fullWidth
                    label={t('Name Copy of Target Population')}
                    required
                    variant="outlined"
                    component={FormikTextField}
                  />
                </Grid>
                <Grid item xs={12}>
                  <ProgramCycleAutocompleteRest
                    value={values.programCycleId}
                    onChange={async (e) => {
                      await setFieldValue('programCycleId', e);
                    }}
                    required
                    error={errors.programCycleId?.value}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button data-cy="button-cancel" onClick={() => setOpen(false)}>
                  {t('CANCEL')}
                </Button>
                <LoadingButton
                  loading={loading}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-target-population-duplicate"
                >
                  {t('Save')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
};
