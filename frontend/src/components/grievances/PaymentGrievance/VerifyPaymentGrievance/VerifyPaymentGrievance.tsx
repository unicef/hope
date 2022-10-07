import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid,
} from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../../../containers/dialogs/Dialog';
import { DialogActions } from '../../../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikRadioGroup } from '../../../../shared/Formik/FormikRadioGroup';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import {
  GrievanceTicketNode,
  GrievanceTicketDocument,
  useUpdateGrievanceMutation,
} from '../../../../__generated__/graphql';

export interface VerifyPaymentGrievanceProps {
  ticket: GrievanceTicketNode;
}
export function VerifyPaymentGrievance({
  ticket,
}: VerifyPaymentGrievanceProps): React.ReactElement {
  const { t } = useTranslation();
  const [VerifyManualDialogOpen, setVerifyManualDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { error }] = useUpdateGrievanceMutation();

  const submit = async (values): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            ticketId: ticket.id,
            extras: {
              ticketPaymentVerificationDetailsExtras: {
                newReceivedAmount: values.newReceivedAmount,
                newStatus: values.newStatus,
              },
            },
          },
        },
        refetchQueries: () => [
          {
            query: GrievanceTicketDocument,
            variables: { id: ticket.id },
          },
        ],
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
    ticketId: ticket.id,
    newReceivedAmount: 0,
    newStatus: 'RECEIVED',
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
            >
              {t('Verify')}
            </Button>
          </Box>
          <Dialog
            open={VerifyManualDialogOpen}
            onClose={() => setVerifyManualDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                {t('Verify Payment')}
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Grid container>
                  <Grid item xs={12}>
                    <Field
                      name='newStatus'
                      label='Status'
                      style={{ flexDirection: 'row' }}
                      choices={[
                        { value: 'RECEIVED', name: t('Received') },
                        { value: 'NOT_RECEIVED', name: t('Not Received') },
                      ]}
                      component={FormikRadioGroup}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    {values.newStatus === 'RECEIVED' && (
                      <Field
                        name='newReceivedAmount'
                        type='number'
                        label={t('Amount Received')}
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
                  {t('CANCEL')}
                </Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={() => submit(values)}
                  data-cy='button-submit'
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
