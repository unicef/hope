import React, { useState } from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  Box,
  Grid,
} from '@material-ui/core';
import styled from 'styled-components';
import { Formik, Form, Field } from 'formik';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { useUpdatePaymentVerificationReceivedAndReceivedAmountMutation } from '../../__generated__/graphql';

export interface Props {
  paymentVerificationId: string;
}
export function VerifyManual({
  paymentVerificationId,
}: Props): React.ReactElement {
  const [VerifyManualDialogOpen, setVerifyManualDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [
    mutate,
    { error },
  ] = useUpdatePaymentVerificationReceivedAndReceivedAmountMutation();

  const DialogTitleWrapper = styled.div`
    border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  `;

  const DialogFooter = styled.div`
    padding: 12px 16px;
    margin: 0;
    border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
    text-align: right;
  `;

  const DialogContainer = styled.div`
    width: 700px;
  `;

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
      showMessage('Payment has been verified.');
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
          <Box p={2}>
            <Button
              color='primary'
              variant='contained'
              onClick={() => setVerifyManualDialogOpen(true)}
              data-cy='button-ed-plan'
            >
              Verify
            </Button>
          </Box>
          <Dialog
            open={VerifyManualDialogOpen}
            onClose={() => setVerifyManualDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>Verify Payment</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Grid container>
                  <Grid item xs={12}>
                    <Field
                      name='status'
                      label='Status'
                      style={{ flexDirection: 'row' }}
                      choices={[
                        { value: 'RECEIVED', name: 'Received' },
                        { value: 'NOT_RECEIVED', name: 'Not Received' },
                      ]}
                      component={FormikRadioGroup}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    {values.status === 'RECEIVED' && (
                      <Field
                        name='receivedAmount'
                        type='number'
                        label='Amount Received'
                        color='primary'
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
                  CANCEL
                </Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={() => submit(values)}
                  data-cy='button-submit'
                >
                  Verify
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}
