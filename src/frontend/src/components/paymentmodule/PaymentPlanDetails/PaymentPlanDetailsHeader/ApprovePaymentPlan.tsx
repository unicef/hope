import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { LoadingButton } from '@core/LoadingButton';
import { GreyText } from '@core/GreyText';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { Action, PaymentPlanQuery } from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { useProgramContext } from '../../../../programContext';

export interface ApprovePaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function ApprovePaymentPlan({
  paymentPlan,
}: ApprovePaymentPlanProps): React.ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();

  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();

  const { mutatePaymentPlanAction: approve, loading: loadingApprove } =
    usePaymentPlanAction(
      Action.Approve,
      paymentPlan.id,
      () => showMessage(t('Payment Plan has been approved.')),
      () => setApproveDialogOpen(false),
    );
  const initialValues = {
    comment: '',
  };

  const validationSchema = Yup.object().shape({
    comment: Yup.string().min(4, 'Too short').max(255, 'Too long'),
  });

  const shouldShowLastApproverMessage = (): boolean => {
    const approvalNumberRequired =
      paymentPlan.approvalProcess?.edges[0]?.node.approvalNumberRequired;

    const approvalsCount =
      paymentPlan.approvalProcess?.edges[0]?.node.actions.approval.length;

    return approvalNumberRequired - 1 === approvalsCount;
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        approve(values.comment);
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <>
          {approveDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <Button
              color="primary"
              variant="contained"
              onClick={() => setApproveDialogOpen(true)}
              data-cy="button-approve"
              disabled={!isActiveProgram}
            >
              {t('Approve')}
            </Button>
          </Box>
          <Dialog
            open={approveDialogOpen}
            onClose={() => setApproveDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Approve Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  {t('Are you sure you want to approve this Payment Plan?')}
                </Box>
                {shouldShowLastApproverMessage() && (
                  <Box p={5}>
                    <GreyText>
                      {t(
                        'Note: You are the last approver. Upon proceeding, this Payment Plan will be automatically moved to authorization stage.',
                      )}
                    </GreyText>
                  </Box>
                )}
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
                <Button onClick={() => setApproveDialogOpen(false)}>
                  CANCEL
                </Button>
                <LoadingButton
                  loading={loadingApprove}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                >
                  {t('Approve')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
