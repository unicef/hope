/* eslint-disable react-hooks/exhaustive-deps */
import {
  Button,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
} from '@material-ui/core';
import ExitToAppRoundedIcon from '@material-ui/icons/ExitToAppRounded';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '../../../containers/dialogs/Dialog';
import { DialogActions } from '../../../containers/dialogs/DialogActions';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { usePassFunctionFromChild } from '../../../hooks/usePassFunctionFromChild';
import { CreateImportFromKoboForm } from './kobo/CreateImportFromKoboForm';
import { CreateImportFromXlsxForm } from './xlsx/CreateImportFromXlsxForm';

const ComboBox = styled(Select)`
  & {
    min-width: 200px;
  }
`;

const StyledInputLabel = styled(InputLabel)`
  background-color: #fff;
`;

const StyledDialogFooter = styled(DialogFooter)`
  && {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
`;

export function RegistrationDataImportCreateDialog(): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [importType, setImportType] = useState('');
  const [submitDisabled, setSubmitDisabled] = useState(true);
  const [submitForm, setSubmitForm] = usePassFunctionFromChild();
  useEffect(() => {
    if (!open) {
      setImportType('');
      setSubmitDisabled(true);
    }
  }, [open]);
  const openModalButton = (
    <span>
      <Button
        variant='contained'
        color='primary'
        startIcon={<ExitToAppRoundedIcon />}
        onClick={() => setOpen(true)}
        data-cy='button-import'
      >
        {t('IMPORT')}
      </Button>
    </span>
  );
  let importTypeForm;
  switch (importType) {
    case 'kobo':
      importTypeForm = (
        <CreateImportFromKoboForm
          setSubmitForm={setSubmitForm}
          setSubmitDisabled={setSubmitDisabled}
        />
      );
      break;
    case 'excel':
      importTypeForm = (
        <CreateImportFromXlsxForm
          setSubmitForm={setSubmitForm}
          setSubmitDisabled={setSubmitDisabled}
        />
      );
      break;
    default:
      importTypeForm = null;
  }

  if (!open) {
    return openModalButton;
  }

  return (
    <span>
      {openModalButton}
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Select File to Import')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <FormControl variant='outlined' margin='dense'>
            <StyledInputLabel>{t('Import From')}</StyledInputLabel>
            <ComboBox
              value={importType}
              defaultValue=''
              variant='outlined'
              label=''
              onChange={(e) => setImportType(e.target.value)}
              fullWidth
              data-cy='import-type-select'
            >
              <MenuItem data-cy='excel-menu-item' key='excel' value='excel'>
                Excel
              </MenuItem>
              <MenuItem data-cy='kobo-menu-item' key='kobo' value='kobo'>
                Kobo
              </MenuItem>
            </ComboBox>
          </FormControl>
          {importTypeForm}
        </DialogContent>
        <StyledDialogFooter data-cy='dialog-actions-container'>
          <Button
            variant='text'
            color='primary'
            component='a'
            href='/api/download-template'
            data-cy='a-download-template'
          >
            {t('DOWNLOAD TEMPLATE')}
          </Button>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <Button
              color='primary'
              variant='contained'
              disabled={submitDisabled}
              data-cy='button-import-rdi'
              onClick={submitForm}
            >
              {t('IMPORT')}
            </Button>
          </DialogActions>
        </StyledDialogFooter>
      </Dialog>
    </span>
  );
}
