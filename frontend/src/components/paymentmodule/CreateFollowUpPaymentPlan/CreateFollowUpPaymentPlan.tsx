import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Typography,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  PaymentPlanQuery,
  useCreateFollowUpPpMutation,
} from '../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { DialogContainer } from '../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { today, tomorrow } from '../../../utils/utils';
import { DividerLine } from '../../core/DividerLine';
import { FieldBorder } from '../../core/FieldBorder';
import { GreyText } from '../../core/GreyText';
import { LabelizedField } from '../../core/LabelizedField';
import { LoadingButton } from '../../core/LoadingButton';
import { Missing } from '../../core/Missing';
import { PermissionDenied } from '../../core/PermissionDenied';

export interface CreateFollowUpPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const CreateFollowUpPaymentPlan = ({
  paymentPlan,
}: CreateFollowUpPaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const [mutate, { loading }] = useCreateFollowUpPpMutation();
  const { showMessage } = useSnackbar();

  const { id } = paymentPlan;

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate: string, schema) =>
          dispersionStartDate &&
          schema.min(
            dispersionStartDate,
            `${t('Dispersion End Date has to be greater than')} ${moment(
              dispersionStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
  });

  type FormValues = Yup.InferType<typeof validationSchema>;
  const initialValues: FormValues = {
    dispersionStartDate: '',
    dispersionEndDate: '',
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
      showMessage(t('Payment Plan Created'), {
        pathname: `/${businessArea}/payment-module/payment-plans/${res.data.createFollowUpPaymentPlan.paymentPlan.id}`,
        historyMethod: 'push',
      });
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
              variant='outlined'
              color='primary'
              onClick={() => setDialogOpen(true)}
            >
              {t('Create Follow-up Payment Plan')}
            </Button>
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll='paper'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Create Follow-up Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  <Box display='flex' flexDirection='column'>
                    <Box mb={2}>
                      <FieldBorder color='#FF0200'>
                        <GreyText>
                          {t(
                            'Follow-up Payment Plan might be started just for unsuccessful payments',
                          )}
                        </GreyText>
                      </FieldBorder>
                    </Box>
                    <Box mb={6}>
                      <FieldBorder color='#FF0200'>
                        <GreyText>
                          {t(
                            'Withdrawn Household cannot be added into follow-up payment plan',
                          )}
                        </GreyText>
                      </FieldBorder>
                    </Box>
                  </Box>

                  <Grid container spacing={3}>
                    <Grid item xs={6}>
                      <Typography>{t('Main Payment Plan Details')}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography>
                        {t('Follow-up Payment Plan Details')}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <LabelizedField label={t('Unsuccessful payments')}>
                        <Missing />
                      </LabelizedField>
                    </Grid>
                    <Grid item xs={6}>
                      <LabelizedField
                        label={t('Payments in follow-up payment plan')}
                      >
                        <Missing />
                      </LabelizedField>
                    </Grid>
                    <Grid item xs={6}>
                      <LabelizedField label={t('Withdrawn Households')}>
                        <Missing />
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
                        name='dispersionStartDate'
                        label={t('Dispersion Start Date')}
                        component={FormikDateField}
                        required
                        disabled={loading}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        data-cy='input-dispersion-start-date'
                        tooltip={t(
                          'The first day from which payments could be delivered.',
                        )}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Field
                        name='dispersionEndDate'
                        label={t('Dispersion End Date')}
                        component={FormikDateField}
                        required
                        minDate={tomorrow}
                        disabled={!values.dispersionStartDate}
                        initialFocusedDate={values.dispersionStartDate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        data-cy='input-dispersion-end-date'
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
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
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
};
