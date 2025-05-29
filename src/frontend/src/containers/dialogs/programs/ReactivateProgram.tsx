import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useUpdateProgramMutation } from '@generated/graphql';
import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useProgramContext } from '../../../programContext';
import { useNavigate } from 'react-router-dom';
import { Status791Enum as ProgramStatus } from '@restgenerated/models/Status791Enum';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';

interface ReactivateProgramProps {
  program: ProgramDetail;
}

export function ReactivateProgram({
  program,
}: ReactivateProgramProps): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();

  const [mutate, { loading }] = useUpdateProgramMutation();
  const reactivateProgram = async (): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          status: ProgramStatus.ACTIVE,
        },
        //TODO: add
        version: null,
        // version: program.version,
      },
    });
    if (!response.errors && response.data.updateProgram) {
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatus.ACTIVE,
      });

      showMessage(t('Programme reactivated.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
      setOpen(false);
    } else {
      showMessage(t('Programme reactivate action failed.'));
    }
  };
  return (
    <span>
      <Button
        data-cy="button-reactivate-program"
        variant="outlined"
        color="primary"
        onClick={() => setOpen(true)}
      >
        {t('Reactivate')}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Reactivate Programme')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to reactivate this Programme?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-cancel" onClick={() => setOpen(false)}>
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={loading}
              type="submit"
              color="primary"
              variant="contained"
              onClick={reactivateProgram}
              data-cy="button-reactivate-program-popup"
            >
              {t('REACTIVATE')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
