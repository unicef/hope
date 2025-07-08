import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import { Formik, Form, Field } from 'formik';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useSnackbar } from '@hooks/useSnackBar';
import { ReactElement } from 'react';
import { showApiErrorMessages } from '@utils/utils';

const RefuseRdiForm = ({
  registration,
  refuseMutate,
  open,
  onClose,
}): ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { name } = registration;
  const initialValues = {
    refuseReason: '',
  };

  const validationSchema = Yup.object().shape({
    refuseReason: Yup.string()
      .min(5, t('Too short'))
      .max(100, t('Too long'))
      .required(t('Refuse reason is required')),
  });

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={async (values) => {
        try {
          await refuseMutate({
            reason: values.refuseReason,
          });
          onClose();
          showMessage('RDI refused');
        } catch (e) {
          showApiErrorMessages(e, showMessage, t('Failed to refuse RDI'));
        }
      }}
    >
      {({ submitForm }) => (
        <Form>
          <Dialog open={open} onClose={onClose} style={{ minWidth: '750px' }}>
            <DialogTitle>Refuse RDI</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Are you sure, that you want to refuse RDI {name}?
              </DialogContentText>
              <Field
                name="refuseReason"
                fullWidth
                multiline
                variant="outlined"
                label={t('RDI Refuse Reason')}
                component={FormikTextField}
              />
            </DialogContent>
            <DialogActions>
              <Button data-cy="button-cancel" onClick={onClose}>
                Cancel
              </Button>
              <Button
                data-cy="button-save"
                onClick={submitForm}
                color="primary"
                variant="contained"
              >
                Save
              </Button>
            </DialogActions>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
};

export { RefuseRdiForm };
