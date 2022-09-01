import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { LookUpPaymentRecordTable } from '../LookUpPaymentRecordTable/LookUpPaymentRecordTable';

export const LookUpPaymentRecordModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): React.ReactElement => {
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
        <>
          <Dialog
            maxWidth='lg'
            fullWidth
            open={lookUpDialogOpen}
            onClose={() => setLookUpDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                {t('Look up Payment Record')}
              </DialogTitle>
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
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  {t('SAVE')}
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
};
