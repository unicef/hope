import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingButton } from '@core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { Field, Form, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from '../../../../../programContext';
import type { PaymentPlanGroupDetail } from '../types';

interface AbortGroupButtonProps {
  group: PaymentPlanGroupDetail;
}

export function AbortGroupButton({
  group,
}: AbortGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { mutate: abort, isPending } = useMutation<void, Error, string>({
    mutationKey: ['abortPaymentPlanGroup', group.id],
    // TODO: call RestService.restBusinessAreasProgramsPaymentPlanGroupsAbortCreate
    // with { id: group.id, requestBody: { abortComment } } once the backend adds it.
    mutationFn: () => Promise.reject(new Error(t('Not available yet'))),
    onSuccess: async () => {
      showMessage(t('Payment Plan Group has been aborted.'));
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
    onError: (error) => showMessage(error.message),
  });

  const validationSchema = Yup.object().shape({
    comment: Yup.string()
      .min(4, 'Too short')
      .max(255, 'Too long')
      .required('Abort Reason is required'),
  });

  return (
    <Formik
      initialValues={{ comment: '' }}
      onSubmit={(values, { resetForm }) => {
        abort(values.comment);
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <>
          {dialogOpen && <AutoSubmitFormOnEnter />}
          <Box sx={{ p: 2 }}>
            <Button
              color="secondary"
              variant="outlined"
              onClick={() => setDialogOpen(true)}
              data-cy="button-abort"
              disabled={!isActiveProgram}
              data-perm={PERMISSIONS.PM_ABORT}
            >
              {t('Abort')}
            </Button>
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Abort Payment Plan Group')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box sx={{ p: 5 }}>
                  {t('Are you sure you want to abort this Payment Plan Group?')}
                </Box>
                <Form>
                  <Field
                    name="comment"
                    multiline
                    fullWidth
                    variant="filled"
                    label={t('Abort Reason')}
                    component={FormikTextField}
                    required
                  />
                </Form>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
                <LoadingButton
                  loading={isPending}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit-abort"
                  data-perm={PERMISSIONS.PM_ABORT}
                >
                  {t('Abort')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
