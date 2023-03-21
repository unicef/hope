import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { usePaymentPlanAction } from '../../../../hooks/usePaymentPlanAction';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField/FormikTextField';
import { Action, PaymentPlanQuery } from '../../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../core/AutoSubmitFormOnEnter';
import { GreyText } from '../../../core/GreyText';
import { LoadingButton } from '../../../core/LoadingButton';

export interface MarkAsReleasedPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const MarkAsReleasedPaymentPlan = ({
  paymentPlan,
}: MarkAsReleasedPaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [markAsReleasedDialogOpen, setMarkAsReleasedDialogOpen] = useState(
    false,
  );
  const { showMessage } = useSnackbar();
  const {
    mutatePaymentPlanAction: review,
    loading: loadingReview,
  } = usePaymentPlanAction(
    Action.Review,
    paymentPlan.id,
    () => showMessage(t('Payment Plan has been marked as reviewed.')),
    () => setMarkAsReleasedDialogOpen(false),
  );

  const shouldShowLastReviewerMessage = (): boolean => {
    const financeReleaseNumberRequired =
      paymentPlan.approvalProcess?.edges[0]?.node.financeReleaseNumberRequired;
    const financeReleasesCount =
      paymentPlan.approvalProcess?.edges[0]?.node.actions.financeRelease.length;

    return financeReleaseNumberRequired - 1 === financeReleasesCount;
  };

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
          review(values.comment);
          resetForm({});
        }}
        validationSchema={validationSchema}
      >
        {({ submitForm }) => (
          <>
            {markAsReleasedDialogOpen && <AutoSubmitFormOnEnter />}
            <Box p={2}>
              <Button
                color='primary'
                variant='contained'
                onClick={() => setMarkAsReleasedDialogOpen(true)}
                data-cy='button-mark-as-released'
              >
                {t('Mark as released')}
              </Button>
            </Box>
            <Dialog
              open={markAsReleasedDialogOpen}
              onClose={() => setMarkAsReleasedDialogOpen(false)}
              scroll='paper'
              aria-labelledby='form-dialog-title'
              maxWidth='md'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title'>
                  {t('Mark as Released')}
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogContainer>
                  <Box p={5}>
                    {t(
                      'Are you sure you want to mark this Payment Plan as released?',
                    )}
                  </Box>
                  {shouldShowLastReviewerMessage() && (
                    <Box p={5}>
                      <GreyText>
                        {t(
                          'Note: You are the last reviewer. Upon proceeding, this Payment Plan will be automatically moved to accepted status',
                        )}
                      </GreyText>
                    </Box>
                  )}
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
                  <Button onClick={() => setMarkAsReleasedDialogOpen(false)}>
                    CANCEL
                  </Button>
                  <LoadingButton
                    loading={loadingReview}
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    {t('Mark as released')}
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
