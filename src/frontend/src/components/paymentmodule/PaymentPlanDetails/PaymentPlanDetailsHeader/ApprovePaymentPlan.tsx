import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { GreyText } from '@core/GreyText';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { AcceptanceProcess } from '@restgenerated/models/AcceptanceProcess';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useProgramContext } from '../../../../programContext';

export interface ApprovePaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function ApprovePaymentPlan({
  paymentPlan,
}: ApprovePaymentPlanProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();

  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: approve, isPending: loadingApprove } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
      requestBody: AcceptanceProcess;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansApproveCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
      }),
    onSuccess: () => {
      showMessage(t('Payment Plan has been approved.'));
      setApproveDialogOpen(false);
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
      });
    },
  });
  const initialValues = {
    comment: '',
  };

  const validationSchema = Yup.object().shape({
    comment: Yup.string().min(4, 'Too short').max(255, 'Too long'),
  });

  const shouldShowLastApproverMessage = (): boolean => {
    const approvalNumberRequired =
      paymentPlan.approvalProcess?.[paymentPlan.approvalProcess.length - 1]
        ?.approvalNumberRequired;

    const approvalsCount =
      paymentPlan.approvalProcess?.[paymentPlan.approvalProcess.length - 1]
        .actions?.approval?.length;

    return approvalNumberRequired - 1 === approvalsCount;
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        approve({
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programSlug: programId,
          requestBody: {
            comment: values.comment,
          },
        });
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
