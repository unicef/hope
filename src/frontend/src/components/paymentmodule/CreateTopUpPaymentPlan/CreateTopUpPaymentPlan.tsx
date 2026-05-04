import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  TextField,
  Typography,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { useMutation } from '@tanstack/react-query';
import { showApiErrorMessages, today, tomorrow } from '@utils/utils';
import { format } from 'date-fns';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import * as Yup from 'yup';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useProgramContext } from '../../../programContext';

export interface CreateTopUpPaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function CreateTopUpPaymentPlan({
  paymentPlan,
}: CreateTopUpPaymentPlanProps): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const { isActiveProgram } = useProgramContext();
  const { showMessage } = useSnackbar();

  const { mutateAsync: createTopUpPaymentPlan, isPending: loadingCreate } =
    useMutation({
      mutationFn: (requestBody: {
        dispersionStartDate: string;
        dispersionEndDate: string;
        totalEntitledQuantityUsd: string;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansCreateTopUpCreate({
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programCode: programId,
          requestBody,
        }),
    });

  if (permissions === null) return null;

  const validationSchema = Yup.object().shape({
    totalEntitledQuantityUsd: Yup.number()
      .required(t('Total Entitled Quantity is required'))
      .positive(t('Total Entitled Quantity must be greater than 0')),
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate: any, schema: Yup.DateSchema) =>
          dispersionStartDate
            ? schema.min(
                new Date(dispersionStartDate),
                `${t('Dispersion End Date has to be greater than')} ${moment(
                  dispersionStartDate,
                ).format('YYYY-MM-DD')}`,
              )
            : schema,
      ),
  });

  type FormValues = Yup.InferType<typeof validationSchema>;
  const initialValues: FormValues = {
    totalEntitledQuantityUsd: undefined,
    dispersionStartDate: null,
    dispersionEndDate: null,
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const dispersionStartDate = values.dispersionStartDate
        ? format(new Date(values.dispersionStartDate), 'yyyy-MM-dd')
        : null;
      const dispersionEndDate = values.dispersionEndDate
        ? format(new Date(values.dispersionEndDate), 'yyyy-MM-dd')
        : null;

      const requestBody = {
        dispersionStartDate,
        dispersionEndDate,
        totalEntitledQuantityUsd: String(values.totalEntitledQuantityUsd),
      };

      const res = await createTopUpPaymentPlan(requestBody);
      setDialogOpen(false);
      showMessage(t('Payment Plan Created'));
      navigate(`/${baseUrl}/payment-module/payment-plans/${res.id}`);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      validateOnChange
      validateOnBlur
    >
      {({ submitForm, values, handleChange, handleBlur, errors, touched }) => (
        <Form>
          <Box p={2}>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setDialogOpen(true)}
              data-perm={PERMISSIONS.PM_CREATE}
              disabled={
                !hasPermissions(PERMISSIONS.PM_CREATE, permissions) ||
                !isActiveProgram
              }
            >
              {t('Create Top-Up PP')}
            </Button>
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll="paper"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Create Top-Up Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  <Box mb={3}>
                    <Typography>{t('Set the Total Amount')}</Typography>
                  </Box>
                  <Grid container spacing={3}>
                    <Grid size={{ xs: 6 }}>
                      <TextField
                        name="totalEntitledQuantityUsd"
                        label={t('Total Entitled Quantity (USD)')}
                        type="number"
                        required
                        fullWidth
                        disabled={loadingCreate}
                        value={values.totalEntitledQuantityUsd ?? ''}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        error={
                          touched.totalEntitledQuantityUsd &&
                          Boolean(errors.totalEntitledQuantityUsd)
                        }
                        helperText={
                          touched.totalEntitledQuantityUsd &&
                          errors.totalEntitledQuantityUsd
                        }
                        inputProps={{ min: 0, step: '0.01' }}
                        data-cy="input-total-entitled-quantity-usd"
                      />
                    </Grid>
                  </Grid>
                  <Box mt={4} mb={3}>
                    <Typography>{t('Set the Dispersion Dates')}</Typography>
                  </Box>
                  <Grid container spacing={3}>
                    <Grid size={{ xs: 6 }}>
                      <Field
                        name="dispersionStartDate"
                        label={t('Dispersion Start Date')}
                        component={FormikDateField}
                        required
                        disabled={loadingCreate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color="disabled" />
                        }
                        data-cy="input-dispersion-start-date"
                        tooltip={t(
                          'The first day from which payments could be delivered.',
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Field
                        name="dispersionEndDate"
                        label={t('Dispersion End Date')}
                        component={FormikDateField}
                        required
                        minDate={tomorrow}
                        disabled={!values.dispersionStartDate}
                        initialFocusedDate={values.dispersionStartDate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color="disabled" />
                        }
                        data-cy="input-dispersion-end-date"
                        tooltip={t(
                          'The last day on which payments could be delivered.',
                        )}
                      />
                    </Grid>
                  </Grid>
                </Box>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setDialogOpen(false)}>
                  {t('Cancel')}
                </Button>
                <LoadingButton
                  loading={loadingCreate}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                >
                  {t('Save')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}
