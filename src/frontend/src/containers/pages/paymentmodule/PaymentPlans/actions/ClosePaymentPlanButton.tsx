import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { GreyText } from '@core/GreyText';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import { PERMISSIONS } from 'src/config/permissions';
import type { PaymentPlanDetail } from '../types';

const WarningBox = styled(Box)`
  border: 1px solid ${({ theme }) => theme.hctPalette.orange};
  border-radius: 4px;
  background-color: #fff8f0;
`;

interface ClosePaymentPlanButtonProps {
  paymentPlan: PaymentPlanDetail;
}

export function ClosePaymentPlanButton({
  paymentPlan,
}: ClosePaymentPlanButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const hasVerification = paymentPlan.hasVerification;

  const { mutate: closePaymentPlan, isPending } = useMutation({
    mutationFn: (closureComment: string | null) =>
      RestService.restBusinessAreasProgramsPaymentPlansCloseCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan.id,
        requestBody: { closureComment },
      }),
    onSuccess: async () => {
      showMessage(t('Payment Plan has been closed.'));
      setDialogOpen(false);
      await Promise.all(
        [
          RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
          RestService.restBusinessAreasProgramsPaymentPlansList,
          RestService.restBusinessAreasProgramsPaymentListsList,
        ].map((fn) =>
          queryClient.invalidateQueries({ queryKey: restQueryKey(fn) }),
        ),
      );
    },
    onError: (error) => showApiErrorMessages(error, showMessage),
  });

  const validationSchema = Yup.object().shape({
    comment: hasVerification
      ? Yup.string()
      : Yup.string().required(
          t('Justification is required to close without verification'),
        ),
  });

  const summary = paymentPlan.closureSummary;
  const summaryRows = [
    {
      label: t('Number of Payment Lists'),
      value: paymentPlan.paymentListsCount,
    },
    {
      label: t('Total number of Households covered'),
      value: summary.totalHouseholdsCount,
    },
    {
      label: t('Total number of individuals covered'),
      value: summary.totalIndividualsCount,
    },
    {
      label: t('Total Entitlement'),
      value: `${paymentPlan.totalEntitledQuantityUsd ?? 0} USD`,
    },
    {
      label: t('Total amount redeemed'),
      value: `${paymentPlan.totalDeliveredQuantityUsd ?? 0} USD`,
    },
    {
      label: t('Total amount undelivered'),
      value: `${paymentPlan.totalUndeliveredQuantityUsd ?? 0} USD`,
    },
    { label: t('Number of payments'), value: summary.numberOfPayments },
    { label: t('Payments Delivered fully'), value: summary.deliveredFully },
    {
      label: t('Payments Delivered partially'),
      value: summary.deliveredPartially,
    },
    { label: t('Payments Not delivered'), value: summary.notDelivered },
    { label: t('Number of verified payments'), value: summary.verified },
    { label: t('Payments verified as received'), value: summary.received },
    {
      label: t('Payments verified as not received'),
      value: summary.notReceived,
    },
    {
      label: t('Payments verified as received with issues'),
      value: summary.receivedWithProblems,
    },
  ];

  return (
    <>
      <Box sx={{ m: 2 }}>
        <Button
          color="primary"
          variant="contained"
          data-cy="button-close"
          onClick={() => setDialogOpen(true)}
          data-perm={PERMISSIONS.PM_CLOSE_FINISHED}
        >
          {t('Close')}
        </Button>
      </Box>
      <Formik
        initialValues={{ comment: '' }}
        validationSchema={validationSchema}
        onSubmit={(values) => closePaymentPlan(values.comment || null)}
      >
        {({ submitForm, values }) => (
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
            fullWidth
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Summary of Payment Plan')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box sx={{ p: 3 }}>
                  <Grid container spacing={2}>
                    {summaryRows.map((row) => (
                      <Grid size={{ xs: 6 }} key={row.label}>
                        <LabelizedField label={row.label} value={row.value} />
                      </Grid>
                    ))}
                  </Grid>
                </Box>
                <Box sx={{ p: 3 }}>
                  {t(
                    'By closing this payment plan you confirm you have verified the information above and considered it correct. Once closed, the payment plan cannot be modified again and all information is considered final.',
                  )}
                </Box>
                {!hasVerification && (
                  <WarningBox sx={{ p: 3, m: 3 }}>
                    <GreyText>
                      {t(
                        'This payment plan has not had any verification carried out. Please include below a justification about closing the payment plan without having carried forward any payment verification.',
                      )}
                    </GreyText>
                    <Form>
                      <Field
                        name="comment"
                        multiline
                        fullWidth
                        variant="filled"
                        label={t('Comment (Mandatory)')}
                        component={FormikTextField}
                      />
                    </Form>
                  </WarningBox>
                )}
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button
                  onClick={() => setDialogOpen(false)}
                  data-cy="button-cancel"
                >
                  {t('Cancel')}
                </Button>
                <LoadingButton
                  loading={isPending}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  disabled={!hasVerification && !values.comment?.trim()}
                  data-cy="button-close-payment-plan"
                >
                  {t('Close Payment Plan')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        )}
      </Formik>
    </>
  );
}
