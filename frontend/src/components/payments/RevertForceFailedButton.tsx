import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Field, Form, Formik } from 'formik';
import * as Yup from 'yup';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useRevertMarkPrAsFailedMutation } from '../../__generated__/graphql';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';

export interface RevertForceFailedButtonProps {
  paymentRecordId: string;
  disabled?: boolean;
}
export function RevertForceFailedButton({
  paymentRecordId,
  disabled = false,
}: RevertForceFailedButtonProps): React.ReactElement {
  const { t } = useTranslation();
  const [isOpenModal, setOpenModal] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useRevertMarkPrAsFailedMutation();

  const validationSchema = Yup.object().shape({
    deliveredQuantity: Yup.number()
      .min(0)
      .max(99999999, t('Number is too big')),
    deliveryDate: Yup.date().required(t('Delivery date is required')),
  });

  const submit = async (values, { resetForm }): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentRecordId,
          deliveredQuantity: values.deliveredQuantity,
          deliveryDate: values.deliveryDate,
        },
      });
      setOpenModal(false);
      showMessage(t('Force failed has been reverted.'));
      resetForm();
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Box>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setOpenModal(true)}
          data-cy='button-revert-mark-as-failed'
          disabled={disabled}
        >
          {t('Revert mark as failed')}
        </Button>
      </Box>
      <Formik
        initialValues={{
          deliveredQuantity: 0,
          deliveryDate: '',
        }}
        validationSchema={validationSchema}
        onSubmit={submit}
      >
        {({ submitForm, resetForm }) => (
          <Dialog
            open={isOpenModal}
            onClose={() => setOpenModal(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Revert mark as failed')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <Form>
                <Field
                  name='deliveredQuantity'
                  label={t('Delivered Quantity')}
                  type='number'
                  required
                  fullWidth
                  variant='outlined'
                  component={FormikTextField}
                />
                <Field
                  name='deliveryDate'
                  label={t('Delivery Date')}
                  component={FormikDateField}
                  required
                  fullWidth
                  decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                />
              </Form>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button
                  onClick={() => {
                    setOpenModal(false);
                    resetForm();
                  }}
                >
                  {t('CANCEL')}
                </Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                  disabled={loading}
                >
                  {t('Revert mark as failed')}
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        )}
      </Formik>
    </Box>
  );
}
