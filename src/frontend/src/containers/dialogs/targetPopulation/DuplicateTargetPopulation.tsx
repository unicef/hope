import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button, DialogContent, DialogTitle, Grid } from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { TargetPopulationCopy } from '@restgenerated/models/TargetPopulationCopy';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { RestService } from '@restgenerated/services/RestService';
import { PaymentPlanGroupAutocompleteRest } from '@shared/autocompletes/rest/PaymentPlanGroupAutocompleteRest';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';
import { FormikChipSelectField } from '@shared/Formik/FormikChipSelectField/FormikChipSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQuery } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import * as Yup from 'yup';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
  programCycleId: Yup.object().shape({
    value: Yup.string().required('Programme Cycle is required'),
  }),
  paymentPlanGroupId: Yup.object().shape({
    value: Yup.string().required('Payment Plan Group is required'),
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
}: DuplicateTargetPopulationProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();

  const { data: programData } = useQuery<ProgramDetail>({
    queryKey: ['programDetail', businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        code: programId,
      }),
  });
  const programPurposes = (programData?.paymentPlanPurposes ?? []).map((p) => ({
    value: p.id,
    name: p.name,
  }));

  const { mutateAsync: mutate, isPending: loading } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      programCode,
      id,
      requestBody,
    }: {
      businessAreaSlug: string;
      programCode: string;
      id: string;
      requestBody: TargetPopulationCopy;
    }) =>
      RestService.restBusinessAreasProgramsTargetPopulationsCopyCreate({
        businessAreaSlug,
        programCode,
        id,
        requestBody,
      }),
  });

  const initialValues = {
    name: '',
    id: targetPopulationId,
    programCycleId: {
      value: '',
      name: '',
    },
    paymentPlanGroupId: {
      value: '',
      name: '',
    },
    paymentPlanPurposes: [] as string[],
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
            const res = (await mutate({
              id: targetPopulationId,
              businessAreaSlug: businessArea,
              programCode: programId,
              requestBody: {
                name: values.name,
                targetPopulationId,
                programCycleId,
                paymentPlanGroupId: values.paymentPlanGroupId.value,
                paymentPlanPurposes: values.paymentPlanPurposes,
              },
            })) as unknown as TargetPopulationDetail;
            setOpen(false);
            showMessage(t('Target Population Duplicated'));
            navigate(`/${baseUrl}/target-population/${res.id}`);
          } catch (e) {
            showApiErrorMessages(
              e,
              showMessage,
              t('Failed to finish programme.'),
            );
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
                <Grid size={{ xs: 12 }}>
                  <Field
                    name="name"
                    fullWidth
                    label={t('Name Copy of Target Population')}
                    required
                    variant="outlined"
                    component={FormikTextField}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <ProgramCycleAutocompleteRest
                    value={values.programCycleId}
                    onChange={async (e) => {
                      await setFieldValue('programCycleId', e);
                      await setFieldValue('paymentPlanGroupId', {
                        value: '',
                        name: '',
                      });
                    }}
                    required
                    error={errors.programCycleId?.value}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <PaymentPlanGroupAutocompleteRest
                    value={values.paymentPlanGroupId}
                    onChange={async (e) => {
                      await setFieldValue('paymentPlanGroupId', e);
                    }}
                    cycleId={values.programCycleId.value}
                    required
                    error={errors.paymentPlanGroupId?.value}
                  />
                </Grid>
                {programPurposes.length > 0 && (
                  <Grid size={{ xs: 12 }}>
                    <Field
                      name="paymentPlanPurposes"
                      label={t('Payment Plan Purposes')}
                      required
                      choices={programPurposes}
                      component={FormikChipSelectField}
                      data-cy="input-payment-plan-purposes"
                    />
                  </Grid>
                )}
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
