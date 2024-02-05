import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import MergeTypeRoundedIcon from '@material-ui/icons/MergeTypeRounded';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  RegistrationDetailedFragment,
  useMergeRdiMutation,
} from '../../../__generated__/graphql';
import { LoadingButton } from '../../core/LoadingButton';
import { useProgramContext } from '../../../programContext';

interface MergeRegistrationDataImportDialogProps {
  registration: RegistrationDetailedFragment;
}

export function MergeRegistrationDataImportDialog({
  registration,
}: MergeRegistrationDataImportDialogProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();

  const [mutate, { loading }] = useMergeRdiMutation({
    variables: { id: registration.id },
  });
  const merge = async (): Promise<void> => {
    const { errors } = await mutate();
    if (errors) {
      showMessage(t('Error while merging Registration Data Import'));
      return;
    }
    showMessage(t('Registration Data Import Merging started'));
  };
  return (
    <span>
      <Button
        startIcon={<MergeTypeRoundedIcon />}
        color="primary"
        variant="contained"
        onClick={() => setOpen(true)}
        disabled={!isActiveProgram}
      >
        {t('Merge')}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Merge Import')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>{t('Are your sure you want to merge this data import?')}</div>
            <div>
              <strong>
                {registration.numberOfHouseholds} {t('households and')}{' '}
                {registration.numberOfIndividuals}{' '}
                {t('individuals will be merged.')}{' '}
              </strong>
              {t('Do you want to proceed?')}
            </div>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={loading}
              type="submit"
              color="primary"
              variant="contained"
              onClick={merge}
            >
              {t('MERGE')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
