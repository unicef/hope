import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField/FormikTextField';
import { LoadingButton } from '../../../core/LoadingButton';
import { GreyText } from '../../../core/GreyText';
import { ErrorButton } from '../../../core/ErrorButton';

export interface MarkAsReviewedPaymentPlanProps {
  paymentPlanId: string;
}

export const MarkAsReviewedPaymentPlan = ({
  paymentPlanId,
}: MarkAsReviewedPaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [markAsReviewedDialogOpen, setMarkAsReviewedDialogOpen] = useState(
    false,
  );

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
  const initialValues = {
    comment: '',
  };

  const validationSchema = Yup.object().shape({
    comment: Yup.string()
      .min(2, 'Too short')
      .max(255, 'Too long'),
  });

  return (
    <>
      <Formik
        initialValues={initialValues}
        onSubmit={(values, { resetForm }) => {
          console.log('MarkAsReviewed');
          resetForm({});
        }}
        validationSchema={validationSchema}
      >
        {({ submitForm }) => (
          <>
            <Box p={2}>
              <Button
                color='primary'
                variant='contained'
                onClick={() => setMarkAsReviewedDialogOpen(true)}
                data-cy='button-lock-plan'
              >
                {t('Mark as reviewed')}
              </Button>
            </Box>
            <Dialog
              open={markAsReviewedDialogOpen}
              onClose={() => setMarkAsReviewedDialogOpen(false)}
              scroll='paper'
              aria-labelledby='form-dialog-title'
              maxWidth='md'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title'>
                  {t('MarkAsReviewed')}
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogContainer>
                  <Box p={5}>
                    {t(
                      'Are you sure you want to mark this Payment Plan as reviewed?',
                    )}
                  </Box>
                  <Box p={5}>
                    <GreyText>
                      {t(
                        'Note: You are the last reviewer. Upon proceeding, this Payment Plan will be automatically moved to accepted status',
                      )}
                    </GreyText>
                  </Box>
                  <Form>
                    <Field
                      name='comment'
                      multiline
                      fullWidth
                      variant='filled'
                      label='Comment (optional)'
                      component={FormikTextField}
                    />
                  </Form>
                </DialogContainer>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setMarkAsReviewedDialogOpen(false)}>
                    CANCEL
                  </Button>
                  <LoadingButton
                    loading
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={() => console.log(paymentPlanId)}
                    data-cy='button-submit'
                  >
                    {t('Mark as reviewed')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </>
        )}
      </Formik>
    </>
  );
};
