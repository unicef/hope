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
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { LoadingButton } from '@core/LoadingButton';
import { GreyText } from '@core/GreyText';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { useProgramContext } from '../../../../programContext';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { AcceptanceProcess } from '@restgenerated/models/AcceptanceProcess';
import { useBaseUrl } from '@hooks/useBaseUrl';

export interface AuthorizePaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function AuthorizePaymentPlan({
  paymentPlan,
}: AuthorizePaymentPlanProps): ReactElement {
  const { t } = useTranslation();
  const [authorizeDialogOpen, setAuthorizeDialogOpen] = useState(false);
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();

  const { showMessage } = useSnackbar();
  const { mutateAsync: authorize, isPending: loadingAuthorize } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
      requestBody: AcceptanceProcess;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansAuthorizeCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
      }),
    onSuccess: () => {
      showMessage(t('Payment Plan has been authorized.'));
      setAuthorizeDialogOpen(false);
    },
  });
  const initialValues = {
    comment: '',
  };

  const validationSchema = Yup.object().shape({
    comment: Yup.string().min(4, 'Too short').max(255, 'Too long'),
  });

  const shouldShowLastAuthorizerMessage = (): boolean => {
    const authorizationNumberRequired =
      paymentPlan.approvalProcess?.[paymentPlan.approvalProcess.length - 1]
        ?.authorizationNumberRequired;

    const authorizationsCount =
      paymentPlan.approvalProcess?.[paymentPlan.approvalProcess.length - 1]
        .actions?.authorization?.length;

    return authorizationNumberRequired - 1 === authorizationsCount;
  };
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        authorize({
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programSlug: programId,
          requestBody: {
            comment: values.comment,
          },
        });
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
