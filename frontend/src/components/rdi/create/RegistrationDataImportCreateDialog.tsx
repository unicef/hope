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
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingComponent } from '../../core/LoadingComponent';
import { Dialog } from '../../../containers/dialogs/Dialog';
import { DialogActions } from '../../../containers/dialogs/DialogActions';
import { usePassFunctionFromChild } from '../../../hooks/usePassFunctionFromChild';
import { CreateImportFromKoboForm } from './kobo/CreateImportFromKoboForm';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const ComboBox = styled(Select)`
  & {
    min-width: 200px;
  }
`;

const StyledInputLabel = styled(InputLabel)`
  background-color: #fff;
`;
const DropzoneContainer = styled.div`
  width: 100%;
  height: 100px;
  background-color: rgba(2, 62, 144, 0.1);
  color: #023e90;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${({ theme }) => theme.spacing(5)}px;
  cursor: pointer;

  ${({ disabled }) => (disabled ? 'filter: grayscale(100%);' : '')}
`;

const StyledDialogFooter = styled(DialogFooter)`
  && {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
`;

function DropzoneField({ onChange, loading }): React.ReactElement {
  const onDrop = useCallback((acceptedFiles) => {
    onChange(acceptedFiles);
  }, []);
  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({
    disabled: loading,
    accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    onDrop,
  });
  const acceptedFilename =
    acceptedFiles.length > 0 ? acceptedFiles[0].name : null;
  return (
    <div>
      <DropzoneContainer {...getRootProps()} disabled={loading}>
        <LoadingComponent isLoading={loading} absolute />
        <input {...getInputProps()} data-cy='rdi-file-input' />
        {acceptedFilename || 'UPLOAD FILE'}
      </DropzoneContainer>
    </div>
  );
}

export function RegistrationDataImportCreateDialog(): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [importType, setImportType] = useState('');
  const [submitDisabled, setSubmitDisabled] = useState(true);
  const [submitForm, setSubmitForm] = usePassFunctionFromChild();
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
    case 'xlsx':
      importTypeForm = null;
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
            >
              <MenuItem key='excel' value='excel'>
                Excel
              </MenuItem>
              <MenuItem key='kobo' value='kobo'>
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
            onClick={() => {
              console.log('test');
            }}
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
              data-cy='button-import'
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
