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
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useProgramContext } from '../../../../programContext';
import { useMutation } from '@tanstack/react-query';

export interface MarkAsReleasedPaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function MarkAsReleasedPaymentPlan({
  paymentPlan,
}: MarkAsReleasedPaymentPlanProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const [markAsReleasedDialogOpen, setMarkAsReleasedDialogOpen] =
    useState(false);
  const { showMessage } = useSnackbar();
  const { mutateAsync: markAsReleased, isPending: loadingMarkAsReleased } =
    useMutation({
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
        RestService.restBusinessAreasProgramsPaymentPlansMarkAsReleasedCreate({
          businessAreaSlug,
          id,
          programSlug,
          requestBody,
        }),
      onSuccess: () => {
        showMessage(t('Payment Plan has been marked as released.'));
        setMarkAsReleasedDialogOpen(false);
      },
    });

  const shouldShowLastReviewerMessage = (): boolean => {
    const financeReleaseNumberRequired =
      paymentPlan.approvalProcess?.[paymentPlan.approvalProcess.length - 1]
        ?.financeReleaseNumberRequired;

    const financeReleasesCount =
      paymentPlan.approvalProcess?.[paymentPlan.approvalProcess.length - 1]
        .actions?.financeRelease?.length;

    return financeReleaseNumberRequired - 1 === financeReleasesCount;
  };

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
        markAsReleased({
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
          {markAsReleasedDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <Button
              color="primary"
              variant="contained"
              onClick={() => setMarkAsReleasedDialogOpen(true)}
              data-cy="button-mark-as-released"
              disabled={!isActiveProgram}
            >
              {t('Mark as released')}
            </Button>
          </Box>
          <Dialog
            open={markAsReleasedDialogOpen}
            onClose={() => setMarkAsReleasedDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Mark as Released')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  {t(
                    'Are you sure you want to mark this Payment Plan as released?',
                  )}
                </Box>
                {shouldShowLastReviewerMessage() && (
                  <Box p={5}>
                    <GreyText>
                      {t(
                        'Note: You are the last reviewer. Upon proceeding, this Payment Plan will be automatically moved to accepted status',
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
                <Button onClick={() => setMarkAsReleasedDialogOpen(false)}>
                  CANCEL
                </Button>
                <LoadingButton
                  loading={loadingMarkAsReleased}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                >
                  {t('Mark as released')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
