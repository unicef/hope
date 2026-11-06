import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { useSnackbar } from '@hooks/useSnackBar';
import EditIcon from '@mui/icons-material/EditRounded';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { Field, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { showApiErrorMessages } from '@utils/utils';
import type { PaymentPlanSettings } from '@components/paymentmodule/PaymentPlanSettingsFields';
import { PaymentPlanSettingsFields } from '@components/paymentmodule/PaymentPlanSettingsFields';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import type { PaymentPlanDetail } from '../types';

interface EditPaymentPlanProps {
  paymentPlan: PaymentPlanDetail | null | undefined;
}

interface EditPaymentPlanValues extends PaymentPlanSettings {
  name: string;
}

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required').max(255),
});

export function EditPaymentPlan({
  paymentPlan,
}: EditPaymentPlanProps): ReactElement | null {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const permissions = usePermissions();
  const { mutateAsync, isPending } = useMutation({
    mutationFn: async (values: EditPaymentPlanValues) =>
      RestService.restBusinessAreasProgramsPaymentPlansUpdate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan?.id ?? '',
        requestBody: {
          id: paymentPlan?.id ?? '',
          unicefId: paymentPlan?.unicefId ?? null,
          name: values.name,
          financialServiceProvider: values.financialServiceProvider,
          currency: values.currency,
          dispersionStartDate: values.dispersionStartDate,
          dispersionEndDate: values.dispersionEndDate,
          version: paymentPlan?.version,
        },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
        ),
      });
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
      });
      // An FSP change rebuilds every payment list in the plan.
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentListsList,
        ),
      });
      setOpen(false);
      showMessage(t('Payment Plan updated'));
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  if (!paymentPlan) return null;
  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_UPDATE, permissions))
    return null;

  return (
    <>
      <Button
        variant="outlined"
        color="primary"
        onClick={() => setOpen(true)}
        startIcon={<EditIcon />}
        data-cy="button-edit-group-name"
      >
        {t('Edit Payment Plan')}
      </Button>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <Formik
          initialValues={{
            name: paymentPlan.name ?? '',
            financialServiceProvider:
              paymentPlan.financialServiceProvider?.id ?? null,
            currency: paymentPlan.currency ?? null,
            dispersionStartDate: paymentPlan.dispersionStartDate ?? null,
            dispersionEndDate: paymentPlan.dispersionEndDate ?? null,
          }}
          validationSchema={validationSchema}
          onSubmit={async (values) => {
            try {
              await mutateAsync(values);
            } catch {
              // handled in onError
            }
          }}
        >
          {({ submitForm, values, setValues }) => (
            <>
              <DialogTitleWrapper>
                <DialogTitle>{t('Edit Payment Plan')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Field
                  name="name"
                  label={t('Name')}
                  component={FormikTextField}
                  fullWidth
                  required
                />
                <Box sx={{ mt: 2 }}>
                  <PaymentPlanSettingsFields
                    value={values}
                    onChange={(settings) =>
                      setValues({ ...values, ...settings })
                    }
                    disabled={paymentPlan.status !== PaymentPlanStatusEnum.OPEN}
                  />
                </Box>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                  <LoadingButton
                    loading={isPending}
                    color="primary"
                    variant="contained"
                    onClick={submitForm}
                    data-cy="button-submit"
                  >
                    {t('Save')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
}
