import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import Edit from '@material-ui/icons/Edit';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveDeleteHouseholdDataChangeMutation,
} from '../../__generated__/graphql';

export interface ApproveDeleteHouseholdGrievanceDetails {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  type: 'edit' | 'button';
}

const EditIcon = styled(Edit)`
  color: ${({ theme }) => theme.hctPalette.darkerBlue};
`;

export const ApproveDeleteHouseholdGrievanceDetails = ({
  ticket,
  type,
}: ApproveDeleteHouseholdGrievanceDetails): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [mutate] = useApproveDeleteHouseholdDataChangeMutation();
  const { showMessage } = useSnackbar();
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const {
    approveStatus,
    reasonHousehold,
  } = ticket.deleteHouseholdTicketDetails;

  const validationSchema = Yup.object().shape({
    reasonHhId: Yup.string().when('withdrawReason', (withdrawReasonValue) => {
      if (withdrawReasonValue === 'duplicate' && !approveStatus) {
        return Yup.string()
          .required('Household Unicef Id is required')
          .max(15, 'Too long');
      }
      return Yup.string();
    }),
  });

  const matchDialogTitle = (): string => {
    if (approveStatus && type !== 'edit') {
      return t('Warning');
    }
    return t('Reason of withdrawal');
  };

  const showWithdraw = (): boolean => {
    if (approveStatus && type === 'edit') {
      return true;
    }
    if (!approveStatus && type === 'button') {
      return true;
    }
    return false;
  };

  return (
    <Formik
      enableReinitialize
      initialValues={{
        withdrawReason: reasonHousehold ? 'duplicate' : 'other',
        reasonHhId: type === 'edit' ? reasonHousehold?.unicefId : '',
      }}
      validationSchema={validationSchema}
      onSubmit={async (values, { resetForm }) => {
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              approveStatus: type === 'edit' ? true : !approveStatus,
              reasonHhId:
                values.withdrawReason === 'duplicate' ? values.reasonHhId : '',
            },
            refetchQueries: () => [
              {
                query: GrievanceTicketDocument,
                variables: { id: ticket.id },
              },
            ],
          });
          if (type === 'edit') {
            showMessage(t('Changes Approved'));
          }
          if (approveStatus) {
            showMessage(t('Changes Disapproved'));
          }
          if (!approveStatus) {
            showMessage(t('Changes Approved'));
          }
          setDialogOpen(false);
          resetForm();
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ values, submitForm, resetForm }) => (
        <>
          <Box p={2}>
            {type === 'edit' ? (
              <IconButton
                data-cy='edit-button'
                onClick={() => setDialogOpen(true)}
              >
                <EditIcon />
              </IconButton>
            ) : (
              <Button
                data-cy='button-approve'
                onClick={() => setDialogOpen(true)}
                variant={approveStatus ? 'outlined' : 'contained'}
                color='primary'
                disabled={!isForApproval}
              >
                {approveStatus ? t('Disapprove') : t('Approve')}
              </Button>
            )}
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle>{matchDialogTitle()}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box display='flex' flexDirection='column'>
                  <Box mt={2}>
                    <Typography variant='body2'>
                      {showWithdraw()
                        ? t(
                            'Please provide the reason of withdrawal of this household.',
                          )
                        : t(
                            'You did not approve the following household to be withdrawn. Are you sure you want to continue?',
                          )}
                    </Typography>
                  </Box>
                  {showWithdraw() && (
                    <Box>
                      <Field
                        name='withdrawReason'
                        choices={[
                          {
                            value: 'duplicate',
                            name:
                              'This household is a duplicate of another household',
                          },
                        ]}
                        component={FormikRadioGroup}
                        noMargin
                      />
                      {values.withdrawReason === 'duplicate' && (
                        <Grid container>
                          <Grid item xs={6}>
                            <Field
                              name='reasonHhId'
                              fullWidth
                              variant='outlined'
                              label={t('Household Unicef Id')}
                              component={FormikTextField}
                              required
                            />
                          </Grid>
                        </Grid>
                      )}
                      <Field
                        name='withdrawReason'
                        choices={[{ value: 'other', name: 'Other' }]}
                        component={FormikRadioGroup}
                        noMargin
                      />
                    </Box>
                  )}
                </Box>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button
                  onClick={() => {
                    setDialogOpen(false);
                    resetForm();
                  }}
                >
                  {t('CANCEL')}
                </Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  {t('Confirm')}
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
};
