import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
} from '@mui/material';
import { PatchedPaymentVerificationUpdate } from '@restgenerated/models/PatchedPaymentVerificationUpdate';
import { RestService } from '@restgenerated/services/RestService';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

export interface Props {
  paymentVerificationId: string;
  status: string;
  enabled: boolean;
  receivedAmount: string;
  verificationPlanId: string;
  paymentId: string;
  paymentPlanId: string;
}

export function VerifyManual({
  paymentVerificationId,
  status,
  enabled,
  receivedAmount,
  verificationPlanId,
  paymentId,
  paymentPlanId,
}: Props): ReactElement {
  const { t } = useTranslation();
  const [verifyManualDialogOpen, setVerifyManualDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const { programSlug, businessAreaSlug } = useBaseUrl();
  const updateVerificationMutation = useMutation({
    mutationFn: (data: PatchedPaymentVerificationUpdate) =>
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsPartialUpdate(
        {
          businessAreaSlug,
          id: paymentId,
          programSlug,
          paymentVerificationPk: verificationPlanId,
          requestBody: data,
        },
      ),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          'payment',
          businessAreaSlug,
          paymentId,
          programSlug,
          paymentPlanId,
        ],
      });
    },
  });

  const submit = async (values): Promise<void> => {
    try {
      await updateVerificationMutation.mutateAsync({
        received: values.status === 'RECEIVED',
        receivedAmount:
          values.status === 'RECEIVED' ? parseFloat(values.receivedAmount) : 0,
      });
      setVerifyManualDialogOpen(false);
      showMessage(t('Payment has been verified.'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const initialValues = {
    paymentVerificationId,
    status: 'RECEIVED',
    receivedAmount: receivedAmount ?? 0,
  };

  return (
    <Formik initialValues={initialValues} onSubmit={submit}>
      {({ values }) => (
        <Form>
          {verifyManualDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <Button
              color="primary"
              variant="contained"
              onClick={() => setVerifyManualDialogOpen(true)}
              data-cy="button-ed-plan"
              disabled={!enabled}
            >
              {status === 'PENDING' ? t('Verify') : t('Edit')}
            </Button>
          </Box>
          <Dialog
            open={verifyManualDialogOpen}
            onClose={() => setVerifyManualDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Verify Payment')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Grid container>
                  <Grid size={{ xs: 12 }}>
                    <Field
                      name="status"
                      label="Status"
                      style={{ flexDirection: 'row' }}
                      choices={[
                        {
                          value: 'RECEIVED',
                          name: t('Received'),
                          dataCy: 'choice-received',
                        },
                        {
                          value: 'NOT_RECEIVED',
                          name: t('Not Received'),
                          dataCy: 'choice-not-received',
                        },
                      ]}
                      component={FormikRadioGroup}
                    />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    {values.status === 'RECEIVED' && (
                      <Field
                        name="receivedAmount"
                        type="number"
                        label={t('Amount Received')}
                        color="primary"
                        component={FormikTextField}
                      />
                    )}
                  </Grid>
                </Grid>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setVerifyManualDialogOpen(false)}>
                  {t('CANCEL')}
                </Button>
                <Button
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={() => submit(values)}
                  data-cy="button-submit"
                >
                  {t('Verify')}
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}
