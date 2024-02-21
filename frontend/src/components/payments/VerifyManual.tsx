import { Box, Button, DialogContent, DialogTitle, Grid } from '@mui/material';
import { Field, Form, Formik } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import {
  PaymentVerificationStatus,
  useUpdatePaymentVerificationReceivedAndReceivedAmountMutation
} from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';

export interface Props {
  paymentVerificationId: string;
  status: string;
  enabled: boolean;
}

export function VerifyManual({
  paymentVerificationId,
  status,
  enabled,
}: Props): React.ReactElement {
  const { t } = useTranslation();
  const [verifyManualDialogOpen, setVerifyManualDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { error }] =
    useUpdatePaymentVerificationReceivedAndReceivedAmountMutation();

  const submit = async (values): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentVerificationId,
          received: values.status === 'RECEIVED',
          receivedAmount:
            values.status === 'RECEIVED'
              ? parseFloat(values.receivedAmount).toFixed(2)
              : 0,
        },
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
      return;
    }
    if (!error) {
      setVerifyManualDialogOpen(false);
      showMessage(t('Payment has been verified.'));
    }
  };

  const initialValues = {
    paymentVerificationId,
    status: 'RECEIVED',
    receivedAmount: 0,
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
              {status === PaymentVerificationStatus.Pending ? t('Verify') : t('Edit')}
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
                  <Grid item xs={12}>
                    <Field
                      name="status"
                      label="Status"
                      style={{ flexDirection: 'row' }}
                      choices={[
                        { value: 'RECEIVED', name: t('Received') },
                        { value: 'NOT_RECEIVED', name: t('Not Received') },
                      ]}
                      component={FormikRadioGroup}
                    />
                  </Grid>
                  <Grid item xs={6}>
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
