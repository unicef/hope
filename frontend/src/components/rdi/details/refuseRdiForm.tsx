import * as React from 'react';
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
import { useSnackbar } from '../../../hooks/useSnackBar';

function RefuseRdiForm({
  registration,
  refuseMutate,
  open,
  onClose,
}): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { id, name } = registration;
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
            variables: {
              id,
              refuseReason: values.refuseReason,
            },
          });
          onClose();
          showMessage('RDI refused');
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
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
              <Button onClick={onClose}>Cancel</Button>
              <Button onClick={submitForm} color="primary" variant="contained">
                Save
              </Button>
            </DialogActions>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}

export { RefuseRdiForm };
