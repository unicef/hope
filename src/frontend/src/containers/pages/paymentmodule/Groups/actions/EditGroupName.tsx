import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { useSnackbar } from '@hooks/useSnackBar';
import EditIcon from '@mui/icons-material/EditRounded';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Field, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { PaymentPlanGroupDetail } from '../types';

interface EditGroupNameProps {
  group: PaymentPlanGroupDetail | null | undefined;
}

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required').max(255),
});

export function EditGroupName({ group }: EditGroupNameProps): ReactElement | null {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const permissions = usePermissions();
  const { mutateAsync, isPending } = useMutation({
    mutationFn: async (name: string) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsUpdate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: group.id,
        requestBody: { id: group.id, unicefId: group.unicefId ?? null, name },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group.id],
      });
      setOpen(false);
      showMessage(t('Group name updated'));
    },
    onError: () => {
      showMessage(t('Failed to update group name'));
    },
  });

  if (!group) return null;
  if (!hasPermissions(PERMISSIONS.PM_UPDATE_PAYMENT_PLAN_GROUP, permissions))
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
          initialValues={{ name: group.name ?? '' }}
          validationSchema={validationSchema}
          onSubmit={async (values) => {
            await mutateAsync(values.name);
          }}
        >
          {({ submitForm }) => (
            <>
              <DialogTitleWrapper>
                <DialogTitle>{t('Edit Group Name')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Field
                  name="name"
                  label={t('Name')}
                  component={FormikTextField}
                  fullWidth
                  required
                />
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
