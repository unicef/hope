/* eslint-disable react-hooks/exhaustive-deps */
import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
} from '@mui/material';
import ExitToAppRoundedIcon from '@mui/icons-material/ExitToAppRounded';
import { ChangeEvent, ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { usePassFunctionFromChild } from '@hooks/usePassFunctionFromChild';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { useProgramContext } from '../../../programContext';
import { CreateImportFromProgramPopulationForm } from './programPopulation/CreateImportFromProgramPopulation';

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

export const RegistrationDataImportCreateDialog = (): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [importType, setImportType] = useState('');
  const [submitDisabled, setSubmitDisabled] = useState(true);
  const [submitForm, setSubmitForm] = usePassFunctionFromChild();
  const { isActiveProgram, selectedProgram } = useProgramContext();
  const programUUID = selectedProgram.id;
  useEffect(() => {
    if (!open) {
      setImportType('');
      setSubmitDisabled(true);
    }
  }, [open]);

  useEffect(() => {
    if (importType === 'programPopulation') {
      setSubmitDisabled(false);
    }
  }, [importType]);

  const openModalButton = (
    <ButtonTooltip
      variant="contained"
      color="primary"
      startIcon={<ExitToAppRoundedIcon />}
      onClick={() => setOpen(true)}
      data-cy="button-import"
      title={t(
        'Program has to be active to create a new RegistrationDataImport',
      )}
      disabled={!isActiveProgram}
    >
      {t('IMPORT')}
    </ButtonTooltip>
  );

  let importTypeForm;
  switch (importType) {
    case 'programPopulation':
      importTypeForm = (
        <CreateImportFromProgramPopulationForm
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
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Select File to Import')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <FormControl variant="outlined">
            <StyledInputLabel size="small" htmlFor="import-type-select">
              {t('Import From')}
            </StyledInputLabel>
            <ComboBox
              id="import-type-select"
              value={importType}
              size="small"
              defaultValue=""
              variant="outlined"
              label=""
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setImportType(e.target.value)
              }
              fullWidth
              data-cy="import-type-select"
            >
              <MenuItem
                data-cy="program-population-menu-item"
                key="program-population"
                value="programPopulation"
              >
                Program Population
              </MenuItem>
            </ComboBox>
          </FormControl>
          <Box mt={2}>{importTypeForm}</Box>
        </DialogContent>
        <StyledDialogFooter data-cy="dialog-actions-container">
          <Button
            variant="text"
            color="primary"
            component="a"
            href={`/api/program/${programUUID}/download-template`}
            data-cy="a-download-template"
          >
            {t('DOWNLOAD TEMPLATE')}
          </Button>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <Button
              color="primary"
              variant="contained"
              disabled={submitDisabled}
              data-cy="button-import-rdi"
              onClick={submitForm}
            >
              {t('IMPORT')}
            </Button>
          </DialogActions>
        </StyledDialogFooter>
      </Dialog>
    </span>
  );
};
