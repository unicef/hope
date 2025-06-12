import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
} from '@mui/material';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { PatchedPaymentVerificationUpdate } from '@restgenerated/models/PatchedPaymentVerificationUpdate';

export interface Props {
  paymentVerificationId: string;
  status: string;
  enabled: boolean;
  receivedAmount: number;
  cashOrPaymentPlanId: string;
  verificationPlanId: string;
}

export function VerifyManual({
  paymentVerificationId,
  status,
  enabled,
  receivedAmount,
  cashOrPaymentPlanId,
  verificationPlanId,
}: Props): ReactElement {
  const { t } = useTranslation();
  const [verifyManualDialogOpen, setVerifyManualDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea, programId: programSlug } = useBaseUrl();

  const updateVerificationMutation = useMutation({
    mutationFn: (data: PatchedPaymentVerificationUpdate) =>
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsPartialUpdate(
        {
          businessAreaSlug: businessArea,
          id: cashOrPaymentPlanId,
          programSlug: programSlug,
          paymentVerificationPk: verificationPlanId,
          requestBody: data,
        },
      ),
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
      showMessage(e.message || t('Failed to verify payment'));
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
