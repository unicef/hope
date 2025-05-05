import { LoadingButton } from '@components/core/LoadingButton';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import { RevertMarkPaymentAsFailed } from '@restgenerated/models/RevertMarkPaymentAsFailed';
import { RestService } from '@restgenerated/services/RestService';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation } from '@tanstack/react-query';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import * as Yup from 'yup';

export interface RevertForceFailedButtonProps {
  paymentId: string;
  disabled?: boolean;
}
export function RevertForceFailedButton({
  paymentId,
  disabled = false,
}: RevertForceFailedButtonProps): ReactElement {
  const { t } = useTranslation();
  const [isOpenModal, setOpenModal] = useState(false);
  const { businessArea, programId } = useBaseUrl();
  const { paymentPlanId } = useParams();
  const { showMessage } = useSnackbar();
  const {
    mutateAsync: revertMarkAsFailed,
    isPending: loadingRevertMarkAsFailed,
  } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      paymentPlanId: ppId,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      paymentPlanId: string;
      programSlug: string;
      requestBody: RevertMarkPaymentAsFailed;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsRevertMarkAsFailedCreate(
        {
          businessAreaSlug,
          paymentId: id,
          paymentPlanId: ppId,
          programSlug,
          requestBody,
        },
      ),
    onSuccess: () => {
      showMessage(t('Force failed has been reverted.'));
    },
    onError: (error) => {
      showMessage(t('Failed to mark the payment as failed.'));
      console.error(error);
    },
  });
  const validationSchema = Yup.object().shape({
    deliveredQuantity: Yup.number()
      .min(0)
      .max(99999999, t('Number is too big')),
    deliveryDate: Yup.date().required(t('Delivery date is required')),
  });

  const submit = (formValues: {
    deliveredQuantity: number;
    deliveryDate: string;
  }): void => {
    revertMarkAsFailed({
      businessAreaSlug: businessArea,
      programSlug: programId,
      paymentPlanId,
      id: paymentId,
      requestBody: {
        deliveredQuantity: formValues.deliveredQuantity,
        deliveryDate: formValues.deliveryDate,
      },
    });
  };

  return (
    <Box>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setOpenModal(true)}
          data-cy="button-revert-mark-as-failed"
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
        onSubmit={(formValues) => submit(formValues)}
      >
        {({ submitForm, resetForm }) => (
          <Dialog
            open={isOpenModal}
            onClose={() => setOpenModal(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Revert mark as failed')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <Form>
                <Field
                  name="deliveredQuantity"
                  label={t('Delivered Quantity')}
                  type="number"
                  required
                  fullWidth
                  variant="outlined"
                  component={FormikTextField}
                />
                <Field
                  name="deliveryDate"
                  label={t('Delivery Date')}
                  component={FormikDateField}
                  required
                  fullWidth
                  decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
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
                <LoadingButton
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                  loading={loadingRevertMarkAsFailed}
                >
                  {t('Revert mark as failed')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        )}
      </Formik>
    </Box>
  );
}
