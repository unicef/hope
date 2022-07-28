import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { GreyText } from '../../../core/GreyText';
import { LoadingButton } from '../../../core/LoadingButton';
import { Missing } from '../../../core/Missing';

export interface LockPaymentPlanProps {
  paymentPlanId: string;
}

export const LockPaymentPlan = ({
  paymentPlanId,
}: LockPaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [lockDialogOpen, setLockDialogOpen] = useState(false);

  const { showMessage } = useSnackbar();
  // const [mutate] = useActivateCashPlanPaymentVerificationMutation();
  // const activate = async (): Promise<void> => {
  //   try {
  //     await mutate({
  //       variables: { cashPlanVerificationId },
  //       refetchQueries,
  //     });
  //   } catch (error) {
  //     /* eslint-disable-next-line no-console */
  //     console.log('error', error?.graphQLErrors);
  //     if (
  //       error?.graphQLErrors?.[0]?.validationErrors
  //         ?.activateCashPlanPaymentVerification?.phone_numbers
  //     ) {
  //       showMessage(
  //         error?.graphQLErrors?.[0]?.validationErrors?.activateCashPlanPaymentVerification?.phone_numbers.join(
  //           '\n',
  //         ),
  //       );
  //     } else {
  //       showMessage(t('Error during activating.'));
  //     }
  //   }

  //   showMessage(t('Verification plan has been activated.'));
  // };
  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setLockDialogOpen(true)}
          data-cy='button-lock-plan'
        >
          {t('Lock')}
        </Button>
      </Box>
      <Dialog
        open={lockDialogOpen}
        onClose={() => setLockDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Lock Payment Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'After you lock this Payment Plan, you will be able to run entitlement formula for selected target population.',
              )}
            </Box>
            <Box p={5}>
              <GreyText>
                {t('Note:')} {t('There are')} <Missing />{' '}
                {t(
                  'households missing payment channel information. Grievance tickets will be automatically created.',
                )}
              </GreyText>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLockDialogOpen(false)}>CANCEL</Button>
            <LoadingButton
              loading
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => console.log(paymentPlanId)}
              data-cy='button-submit'
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
