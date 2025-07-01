import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from '../../../programContext';
import { RegistrationDataImportDetail } from '@restgenerated/models/RegistrationDataImportDetail';
import { useActionMutation } from '@hooks/useActionMutation';
import { RestService } from '@restgenerated/services/RestService';

interface RerunDedupeProps {
  registration: RegistrationDataImportDetail;
}

export const RerunDedupe = ({
  registration,
}: RerunDedupeProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { mutateAsync: mutate, isPending: loading } = useActionMutation(
    registration.id,
    RestService.restBusinessAreasProgramsRegistrationDataImportsDeduplicateCreate,
    [RestService.restBusinessAreasProgramsRegistrationDataImportsRetrieve.name],
  );
  const rerunDedupe = async (): Promise<void> => {
    try {
      await mutate();
      showMessage('Rerunning Deduplication started');
      setOpen(false);
    } catch (e) {
      showMessage(e.message);
    }
  };
  return (
    <span>
      <Button
        color="primary"
        variant="contained"
        onClick={() => setOpen(true)}
        disabled={!isActiveProgram}
        data-cy="button-rerun-dedupe"
      >
        {t('Rerun Deduplication')}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Rerun Deduplication')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>{t('Are your sure you want to rerun deduplication?')}</div>
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
              data-cy="button-rerun-dedupe-confirm"
              onClick={rerunDedupe}
            >
              {t('Rerun')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
};
