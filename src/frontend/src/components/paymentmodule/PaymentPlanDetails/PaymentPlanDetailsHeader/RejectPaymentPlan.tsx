import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Field, Form, Formik } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { Action } from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { ErrorButton } from '@core/ErrorButton';
import { GreyText } from '@core/GreyText';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from '../../../../programContext';

export interface RejectPaymentPlanProps {
  paymentPlanId: string;
}

export function RejectPaymentPlan({
  paymentPlanId,
}: RejectPaymentPlanProps): React.ReactElement {
  const { t } = useTranslation();
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { mutatePaymentPlanAction: reject, loading: loadingReject } =
    usePaymentPlanAction(
      Action.Reject,
      paymentPlanId,
      () => showMessage(t('Payment Plan has been rejected.')),
      () => setRejectDialogOpen(false),
    );

  const initialValues = {
    comment: '',
  };

  const validationSchema = Yup.object().shape({
    comment: Yup.string().min(4, 'Too short').max(255, 'Too long'),
  });

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        reject(values.comment);
        setRejectDialogOpen(false);
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <>
          {rejectDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <ErrorButton
              data-cy="button-reject"
              onClick={() => setRejectDialogOpen(true)}
            >
              {t('Reject')}
            </ErrorButton>
          </Box>
          <Dialog
            open={rejectDialogOpen}
            onClose={() => setRejectDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Reject Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  {t('Are you sure you want to reject this payment plan?')}
                </Box>
                <Box p={5}>
                  <GreyText>
                    {t(
                      'Note: Upon proceeding this payment plan will be automatically moved to locked status.',
                    )}
                  </GreyText>
                </Box>
                <Form>
                  <Field
                    name="comment"
                    multiline
                    fullWidth
                    variant="filled"
                    label="Comment (optional)"
                    component={FormikTextField}
                  />
                </Form>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setRejectDialogOpen(false)}>
                  CANCEL
                </Button>
                <LoadingButton
                  loading={loadingReject}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                  disabled={!isActiveProgram}
                >
                  {t('Reject')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
