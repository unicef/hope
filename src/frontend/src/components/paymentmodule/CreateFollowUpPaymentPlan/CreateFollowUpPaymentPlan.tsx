import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Typography,
} from '@mui/material';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useNavigate } from 'react-router-dom';
import {
  PaymentPlanQuery,
  useCreateFollowUpPpMutation,
} from '@generated/graphql';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { today, tomorrow } from '@utils/utils';
import { DividerLine } from '@core/DividerLine';
import { FieldBorder } from '@core/FieldBorder';
import { GreyText } from '@core/GreyText';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from '../../../programContext';

export interface CreateFollowUpPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function CreateFollowUpPaymentPlan({
  paymentPlan,
}: CreateFollowUpPaymentPlanProps): React.ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const [mutate, { loading }] = useCreateFollowUpPpMutation();
  const { isActiveProgram } = useProgramContext();
  const { showMessage } = useSnackbar();

  const { id, totalWithdrawnHouseholdsCount, unsuccessfulPaymentsCount } =
    paymentPlan;

  if (permissions === null) return null;

  const validationSchema = Yup.object().shape({
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
    dispersionStartDate: null,
    dispersionEndDate: null,
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          paymentPlanId: id,
          dispersionStartDate: values.dispersionStartDate,
          dispersionEndDate: values.dispersionEndDate,
        },
      });
      setDialogOpen(false);
      showMessage(t('Payment Plan Created'));
      navigate(
        `/${baseUrl}/payment-module/followup-payment-plans/${res.data.createFollowUpPaymentPlan.paymentPlan.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
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
      {({ submitForm, values }) => (
        <Form>
          <Box p={2}>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setDialogOpen(true)}
              disabled={
                !hasPermissions(PERMISSIONS.PM_CREATE, permissions) ||
                !isActiveProgram
              }
            >
              {t('Create Follow-up PP')}
            </Button>
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll="paper"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Create Follow-up Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  <Box display="flex" flexDirection="column">
                    {unsuccessfulPaymentsCount === 0 && (
                      <Box mb={2}>
                        <FieldBorder color="#FF0200">
                          <GreyText>
                            {t(
                              'Follow-up Payment Plan might be started just for unsuccessful payments',
                            )}
                          </GreyText>
                        </FieldBorder>
                      </Box>
                    )}
                    {totalWithdrawnHouseholdsCount > 0 && (
                      <Box mb={4}>
                        <FieldBorder color="#FF0200">
                          <GreyText>
                            {t(
                              'Withdrawn Household cannot be added into follow-up payment plan',
                            )}
                          </GreyText>
                        </FieldBorder>
                      </Box>
                    )}
                  </Box>
                  <Grid container spacing={3}>
                    <Grid item xs={6}>
                      <Box mt={2}>
                        <Typography>
                          {t('Main Payment Plan Details')}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} />
                    {/* //TODO: Figure it out */}
                    {/* <Grid item xs={6}>
                      <Typography>
                        {t('Follow-up Payment Plan Details')}
                      </Typography>
                    </Grid> */}
                    <Grid item xs={6}>
                      <LabelizedField label={t('Unsuccessful payments')}>
                        {unsuccessfulPaymentsCount}
                      </LabelizedField>
                    </Grid>
                    {/* <Grid item xs={6}>
                      <LabelizedField
                        label={t('Payments in follow-up payment plan')}
                      >
                        <Missing />
                      </LabelizedField>
                    </Grid> */}
                    <Grid item xs={6}>
                      <LabelizedField label={t('Withdrawn Households')}>
                        {totalWithdrawnHouseholdsCount}
                      </LabelizedField>
                    </Grid>
                  </Grid>
                  <Grid item xs={12}>
                    <DividerLine />
                  </Grid>
                  <Box mb={3}>
                    <Typography>{t('Set the Dispersion Dates')}</Typography>
                  </Box>
                  <Grid container spacing={3}>
                    <Grid item xs={6}>
                      <Field
                        name="dispersionStartDate"
                        label={t('Dispersion Start Date')}
                        component={FormikDateField}
                        required
                        disabled={loading}
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
                    <Grid item xs={6}>
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
                  loading={loading}
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
