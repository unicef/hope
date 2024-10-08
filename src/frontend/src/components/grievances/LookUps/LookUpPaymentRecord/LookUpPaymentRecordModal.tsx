import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Formik } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LookUpPaymentRecordTable } from '../LookUpPaymentRecordTable/LookUpPaymentRecordTable';

export function LookUpPaymentRecordModal({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): React.ReactElement {
  const { t } = useTranslation();
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        onValueChange('selectedPaymentRecords', values.selectedPaymentRecords);
        setLookUpDialogOpen(false);
      }}
    >
      {({ submitForm, setFieldValue }) => (
        <Dialog
          maxWidth="lg"
          fullWidth
          open={lookUpDialogOpen}
          onClose={() => setLookUpDialogOpen(false)}
          scroll="paper"
          aria-labelledby="form-dialog-title"
        >
          {lookUpDialogOpen && <AutoSubmitFormOnEnter />}
          <DialogTitleWrapper>
            <DialogTitle>{t('Look up Payment Record')}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpPaymentRecordTable
              openInNewTab
              setFieldValue={setFieldValue}
              initialValues={initialValues}
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button onClick={() => setLookUpDialogOpen(false)}>
                {t('CANCEL')}
              </Button>
              <Button
                type="submit"
                color="primary"
                variant="contained"
                onClick={submitForm}
                data-cy="button-submit"
              >
                {t('SAVE')}
              </Button>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
}
