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
import type { PaymentPlanGroupDetail } from '../types';

const WarningBox = styled(Box)`
  border: 1px solid ${({ theme }) => theme.hctPalette.orange};
  border-radius: 4px;
  background-color: #fff8f0;
`;

interface CloseGroupButtonProps {
  group: PaymentPlanGroupDetail;
}

export function CloseGroupButton({
  group,
}: CloseGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  // TODO: read from the group once it exposes its verification plans.
  const hasVerification = false;

  const { mutate: closeGroup, isPending } = useMutation({
    mutationFn: (closureComment: string | null) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCloseCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: group.id,
        requestBody: { closureComment },
      }),
    onSuccess: async () => {
      showMessage(t('Payment Plan Group has been closed.'));
      setDialogOpen(false);
      await Promise.all(
        [
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
          RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
          RestService.restBusinessAreasProgramsPaymentPlansList,
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

  // TODO: add the reconciliation and verification rows (payments delivered
  // fully / partially / not delivered, verified as received ...) once the group exposes them.
  const summaryRows = [
    { label: t('Number of Payment Plans'), value: group.paymentPlansCount },
    {
      label: t('Total Entitlement'),
      value: `${group.totalEntitledQuantityUsd ?? 0} USD`,
    },
    {
      label: t('Total amount redeemed'),
      value: `${group.totalDeliveredQuantityUsd ?? 0} USD`,
    },
    {
      label: t('Total amount undelivered'),
      value: `${group.totalUndeliveredQuantityUsd ?? 0} USD`,
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
        onSubmit={(values) => closeGroup(values.comment || null)}
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
              <DialogTitle>{t('Summary of Payment Plan Group')}</DialogTitle>
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
                    'By closing this payment plan group you confirm you have verified the information above and considered it correct. Once closed, the payment plan group cannot be modified again and all information is considered final.',
                  )}
                </Box>
                {!hasVerification && (
                  <WarningBox sx={{ p: 3, m: 3 }}>
                    <GreyText>
                      {t(
                        'This payment plan group has not had any verification carried out. Please include below a justification about closing the payment plan group without having carried forward any payment verification.',
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
                  data-cy="button-close-payment-plan-group"
                >
                  {t('Close Payment Plan Group')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        )}
      </Formik>
    </>
  );
}
