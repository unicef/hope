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
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentVerificationPlan } from '@restgenerated/models/PaymentVerificationPlan';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { showApiErrorMessages } from '@utils/utils';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Field, Form, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';

const WarningBox = styled(Box)`
  border: 1px solid ${({ theme }) => theme.hctPalette.orange};
  border-radius: 4px;
  background-color: #fff8f0;
`;

export interface ClosePaymentPlanDialogProps {
  paymentPlan: PaymentPlanDetail;
  open: boolean;
  onClose: () => void;
}

export function ClosePaymentPlanDialog({
  paymentPlan,
  open,
  onClose,
}: ClosePaymentPlanDialogProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const verificationPlans = paymentPlan.paymentVerificationPlans ?? [];
  const sumBy = (
    selector: (plan: PaymentVerificationPlan) => number | null | undefined,
  ): number =>
    verificationPlans.reduce((acc, plan) => acc + (selector(plan) ?? 0), 0);
  const hasVerification = verificationPlans.some(
    (plan) => (plan.respondedCount ?? 0) > 0,
  );

  const { deliveredFully, deliveredPartially, notDelivered, numberOfPayments } =
    paymentPlan.reconciliationSummary ?? {};

  const { mutateAsync: closePaymentPlan, isPending } = useMutation({
    mutationFn: (closureComment: string | null) =>
      RestService.restBusinessAreasProgramsPaymentPlansCloseCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan.id,
        requestBody: { closureComment },
      }),
    onSuccess: () => {
      showMessage(t('Payment Plan has been closed.'));
      onClose();
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const validationSchema = Yup.object().shape({
    comment: hasVerification
      ? Yup.string()
      : Yup.string().required(
          t('Justification is required to close without verification'),
        ),
  });

  const summaryRows = [
    {
      label: t('Total number of Households covered'),
      value: paymentPlan.totalHouseholdsCount,
    },
    {
      label: t('Total number of individuals covered'),
      value: paymentPlan.totalIndividualsCount,
    },
    {
      label: t('Total Entitlement'),
      value: `${paymentPlan.totalEntitledQuantityUsd ?? 0} USD`,
    },
    {
      label: t('Total amount redeemed'),
      value: `${paymentPlan.totalDeliveredQuantityUsd ?? 0} USD`,
    },
    { label: t('Number of payments'), value: numberOfPayments },
    { label: t('Payments Delivered fully'), value: deliveredFully },
    { label: t('Payments Delivered partially'), value: deliveredPartially },
    { label: t('Payments Not delivered'), value: notDelivered },
    {
      label: t('Number of verified payments'),
      value: sumBy((plan) => plan.respondedCount),
    },
    {
      label: t('Payments verified as received'),
      value: sumBy((plan) => plan.receivedCount),
    },
    {
      label: t('Payments verified as not received'),
      value: sumBy((plan) => plan.notReceivedCount),
    },
    {
      label: t('Payments verified as received with issues'),
      value: sumBy((plan) => plan.receivedWithProblemsCount),
    },
  ];

  return (
    <Formik
      initialValues={{ comment: '' }}
      validationSchema={validationSchema}
      onSubmit={(values) =>
        closePaymentPlan(values.comment ? values.comment : null)
      }
    >
      {({ submitForm, values }) => (
        <Dialog
          open={open}
          onClose={onClose}
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
              <Box p={3}>
                <Grid container spacing={2}>
                  {summaryRows.map((row) => (
                    <Grid size={{ xs: 6 }} key={row.label}>
                      <LabelizedField label={row.label} value={row.value} />
                    </Grid>
                  ))}
                </Grid>
              </Box>
              <Box p={3}>
                {t(
                  'By closing this payment plan you confirm you have verified the information above and considered it correct. Once closed, the payment plan cannot be modified again and all information is considered final.',
                )}
              </Box>
              {!hasVerification && (
                <WarningBox p={3} m={3}>
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
              <Button onClick={onClose} data-cy="button-cancel">
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
  );
}
