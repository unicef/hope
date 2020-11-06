import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { LookUpPaymentRecordTable } from '../LookUpPaymentRecordTable/LookUpPaymentRecordTable';
import { LookUpButton } from '../LookUpButton';
import { Formik } from 'formik';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const LookUpPaymentRecordModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): React.ReactElement => {
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        onValueChange('selectedPaymentRecords', values.selectedPaymentRecords);
        setLookUpDialogOpen(false);
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
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
                Look up Payment Record
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
                  CANCEL
                </Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  SAVE
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
};
