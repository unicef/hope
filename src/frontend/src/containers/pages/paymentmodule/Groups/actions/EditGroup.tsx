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
import type { PaymentPlanGroupSettings } from '@components/paymentmodule/PaymentPlanGroupSettingsFields';
import { PaymentPlanGroupSettingsFields } from '@components/paymentmodule/PaymentPlanGroupSettingsFields';
import type { PaymentPlanGroupDetail } from '../types';

interface EditGroupProps {
  group: PaymentPlanGroupDetail | null | undefined;
}

interface EditGroupValues extends PaymentPlanGroupSettings {
  name: string;
}

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required').max(255),
});

export function EditGroup({ group }: EditGroupProps): ReactElement | null {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const permissions = usePermissions();
  const { mutateAsync, isPending } = useMutation({
    mutationFn: async (values: EditGroupValues) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsUpdate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: group?.id ?? '',
        requestBody: {
          id: group?.id ?? '',
          unicefId: group?.unicefId ?? null,
          name: values.name,
          financialServiceProvider: values.financialServiceProvider,
          currency: values.currency,
        },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
        ),
      });
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
        ),
      });
      setOpen(false);
      showMessage(t('Group updated'));
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  if (!group) return null;
  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_UPDATE, permissions))
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
        {t('Edit Group')}
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
            name: group.name ?? '',
            financialServiceProvider:
              group.financialServiceProvider?.id ?? null,
            currency: group.currency ?? null,
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
                <DialogTitle>{t('Edit Group')}</DialogTitle>
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
                  <PaymentPlanGroupSettingsFields
                    value={values}
                    onChange={(settings) =>
                      setValues({ ...values, ...settings })
                    }
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
