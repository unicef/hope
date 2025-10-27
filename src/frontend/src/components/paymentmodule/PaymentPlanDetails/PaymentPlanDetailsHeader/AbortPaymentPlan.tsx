import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
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
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useProgramContext } from '../../../../programContext';

export interface AbortPaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function AbortPaymentPlan({
  paymentPlan,
}: AbortPaymentPlanProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();

  const [abortDialogOpen, setAbortDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: abort, isPending: loadingAbort } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
      requestBody: { comment?: string };
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansAbortCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
      }),
    onSuccess: () => {
      showMessage(t('Payment Plan has been aborted.'));
      setAbortDialogOpen(false);
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

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        abort({
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
          {abortDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <Button
              color="error"
              variant="contained"
              onClick={() => setAbortDialogOpen(true)}
              data-cy="button-abort"
              disabled={!isActiveProgram}
            >
              {t('Abort')}
            </Button>
          </Box>
          <Dialog
            open={abortDialogOpen}
            onClose={() => setAbortDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Abort Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  {t('Are you sure you want to abort this Payment Plan?')}
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
                <Button onClick={() => setAbortDialogOpen(false)}>
                  CANCEL
                </Button>
                <LoadingButton
                  loading={loadingAbort}
                  type="submit"
                  color="error"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit-abort"
                >
                  {t('Abort')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
