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
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { PatchedUpdateGrievanceTicket } from '@restgenerated/models/PatchedUpdateGrievanceTicket';
import { RestService } from '@restgenerated/services/RestService';
import { showApiErrorMessages } from '@utils/utils';

export interface VerifyPaymentGrievanceProps {
  ticket: GrievanceTicketDetail;
}
export function VerifyPaymentGrievance({
  ticket,
}: VerifyPaymentGrievanceProps): ReactElement {
  const { t } = useTranslation();
  const [verifyManualDialogOpen, setVerifyManualDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();

  const { mutateAsync: mutate } = useMutation({
    mutationFn: (values: any) => {
      const requestBody: PatchedUpdateGrievanceTicket = {
        extras: {
          ticketPaymentVerificationDetailsExtras: {
            newReceivedAmount: values.newReceivedAmount,
            newStatus: values.newStatus,
          },
        },
      };

      return RestService.restBusinessAreasGrievanceTicketsPartialUpdate({
        businessAreaSlug: businessArea,
        id: ticket.id,
        formData: requestBody,
      });
    },
    onSuccess: () => {
      setVerifyManualDialogOpen(false);
      showMessage(t('Payment has been verified.'));
      queryClient.invalidateQueries({
        queryKey: ['GrievanceTicketDetail', ticket.id],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const submit = async (values): Promise<void> => {
    try {
      await mutate(values);
    } catch (e) {
      // Error handling is already in the mutation onError callback
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
          {verifyManualDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <Button
              color="primary"
              variant="contained"
              data-cy="grievance-verify"
              onClick={() => setVerifyManualDialogOpen(true)}
            >
              {t('Verify')}
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
                      name="newStatus"
                      label="Status"
                      style={{ flexDirection: 'row' }}
                      choices={[
                        { value: 'RECEIVED', name: t('Received') },
                        { value: 'NOT_RECEIVED', name: t('Not Received') },
                      ]}
                      component={FormikRadioGroup}
                    />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    {values.newStatus === 'RECEIVED' && (
                      <Field
                        name="newReceivedAmount"
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
