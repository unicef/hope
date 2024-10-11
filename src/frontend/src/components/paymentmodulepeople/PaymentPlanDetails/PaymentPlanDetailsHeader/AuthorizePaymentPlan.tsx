import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { LoadingButton } from '@core/LoadingButton';
import { GreyText } from '@core/GreyText';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { Action, PaymentPlanQuery } from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { useProgramContext } from '../../../../programContext';

export interface AuthorizePaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function AuthorizePaymentPlan({
  paymentPlan,
}: AuthorizePaymentPlanProps): React.ReactElement {
  const { t } = useTranslation();
  const [authorizeDialogOpen, setAuthorizeDialogOpen] = useState(false);
  const { isActiveProgram } = useProgramContext();

  const { showMessage } = useSnackbar();
  const { mutatePaymentPlanAction: authorize, loading: loadingAuthorize } =
    usePaymentPlanAction(
      Action.Authorize,
      paymentPlan.id,
      () => showMessage(t('Payment Plan has been authorized.')),
      () => setAuthorizeDialogOpen(false),
    );
  const initialValues = {
    comment: '',
  };

  const validationSchema = Yup.object().shape({
    comment: Yup.string().min(4, 'Too short').max(255, 'Too long'),
  });

  const shouldShowLastAuthorizerMessage = (): boolean => {
    const authorizationNumberRequired =
      paymentPlan.approvalProcess?.edges[0]?.node.authorizationNumberRequired;

    const authorizationsCount =
      paymentPlan.approvalProcess?.edges[0]?.node.actions.authorization.length;

    return authorizationNumberRequired - 1 === authorizationsCount;
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        authorize(values.comment);
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <>
          {authorizeDialogOpen && <AutoSubmitFormOnEnter />}
          <Box p={2}>
            <Button
              color="primary"
              variant="contained"
              onClick={() => setAuthorizeDialogOpen(true)}
              data-cy="button-authorize"
              disabled={!isActiveProgram}
            >
              {t('Authorize')}
            </Button>
          </Box>
          <Dialog
            open={authorizeDialogOpen}
            onClose={() => setAuthorizeDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Authorize')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box p={5}>
                  {t('Are you sure you want to authorize this Payment Plan?')}
                </Box>
                {shouldShowLastAuthorizerMessage() && (
                  <Box p={5}>
                    <GreyText>
                      {t(
                        'Note: Upon Proceeding, this Payment Plan will be automatically moved to Finance Release stage.',
                      )}
                    </GreyText>
                  </Box>
                )}
                <Form>
                  <Field
                    name="comment"
                    multiline
                    fullWidth
                    variant="filled"
                    label="Comment (optional)"
                    component={FormikTextField}
                  />
                </Form>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setAuthorizeDialogOpen(false)}>
                  CANCEL
                </Button>
                <LoadingButton
                  loading={loadingAuthorize}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                >
                  {t('Authorize')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
