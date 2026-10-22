import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import ReorderIcon from '@mui/icons-material/Reorder';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@mui/material';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import type { SplitPaymentPlan } from '@restgenerated/models/SplitPaymentPlan';
import { RestService } from '@restgenerated/services/RestService';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toApiError } from '@utils/errors';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';

const MIN_PAYMENTS_NO = 10;

interface FormValues {
  splitType: string;
  paymentsNo: number;
}

const initialValues: FormValues = {
  splitType: '',
  paymentsNo: 0,
};

interface SplitGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

/** Splits every plan of the group the same way; a plan smaller than the chunk stays one part. */
export function SplitGroupButton({
  group,
}: SplitGroupButtonProps): ReactElement | null {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const permissions = usePermissions();
  const { mutateAsync: split, isPending: loading } = useMutation({
    mutationFn: (requestBody: SplitPaymentPlan) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsSplitCreate({
        businessAreaSlug: businessArea,
        id: group?.id,
        programCode: programId,
        requestBody,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
        ),
      });
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
      });
    },
  });

  if (!group || group.status !== PaymentPlanGroupStatusEnum.ACCEPTED)
    return null;
  if (!hasPermissions(PERMISSIONS.PM_SPLIT, permissions)) return null;

  const validationSchema = Yup.object().shape({
    splitType: Yup.string().required(t('Split Type is required')),
    paymentsNo: Yup.number().when('splitType', {
      is: 'BY_RECORDS',
      then: (schema) =>
        schema.required(t('Payments Number is required')).min(
          MIN_PAYMENTS_NO,
          t('Payments Number must be greater than {{min}}', {
            min: MIN_PAYMENTS_NO,
          }),
        ),
    }),
  });

  const handleSplit = async (values: FormValues): Promise<void> => {
    try {
      await split({
        splitType: values.splitType as SplitPaymentPlan['splitType'],
        paymentsNo:
          values.splitType === 'BY_RECORDS' ? values.paymentsNo : undefined,
      });
      setDialogOpen(false);
      showMessage(t('Split was successful!'));
    } catch (e) {
      showApiErrorMessages(
        toApiError(e),
        showMessage,
        t('Failed to split the Payment Plan'),
      );
    }
  };

  return (
    <Box sx={{ m: 2 }}>
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handleSplit}
      >
        {({ values, submitForm }) => (
          <Form>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setDialogOpen(true)}
              endIcon={<ReorderIcon />}
              disabled={!group.canSplit}
              data-cy="button-split-group"
              data-perm={PERMISSIONS.PM_SPLIT}
            >
              {t('Split')}
            </Button>
            <Dialog
              open={dialogOpen}
              onClose={() => setDialogOpen(false)}
              scroll="paper"
              aria-labelledby="form-dialog-title"
              maxWidth="md"
            >
              <DialogTitleWrapper>
                <DialogTitle>{t('Split into Payment Lists')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogContainer>
                  <Grid container spacing={3}>
                    <Grid size={{ xs: 12 }}>
                      <Field
                        name="splitType"
                        label={t('Split Type')}
                        choices={group.splitChoices}
                        component={FormikSelectField}
                      />
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                      {values.splitType === 'BY_RECORDS' && (
                        <Field
                          name="paymentsNo"
                          label={t('Payments Number')}
                          component={FormikTextField}
                          type="number"
                          variant="outlined"
                        />
                      )}
                    </Grid>
                  </Grid>
                </DialogContainer>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setDialogOpen(false)}>
                    {t('Cancel')}
                  </Button>
                  <LoadingButton
                    loading={loading}
                    color="primary"
                    variant="contained"
                    onClick={submitForm}
                    data-cy="button-split"
                  >
                    {t('Split')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </Form>
        )}
      </Formik>
    </Box>
  );
}
