import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useUpdateProgramMutation } from '@generated/graphql';
import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useProgramContext } from '../../../programContext';
import { useNavigate } from 'react-router-dom';
import { Status791Enum as ProgramStatus } from '@restgenerated/models/Status791Enum';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';

interface FinishProgramProps {
  program: ProgramDetail;
}

export function FinishProgram({ program }: FinishProgramProps): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();

  const [mutate, { loading }] = useUpdateProgramMutation();
  const finishProgram = async (): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          status: ProgramStatus.FINISHED,
        },
        //TODO: add
        version: null,
        // version: program.version,
      },
    });
    if (!response.errors && response.data.updateProgram) {
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatus.FINISHED,
      });

      showMessage(t('Programme finished.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
      setOpen(false);
    } else {
      showMessage(t('Programme finish action failed.'));
    }
  };
  return (
    <span>
      <Button
        color="primary"
        onClick={() => setOpen(true)}
        data-cy="button-finish-program"
      >
        {t('Finish Programme')}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Finish Programme')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to finish this Programme?')}
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
              onClick={finishProgram}
              data-cy="button-finish-program"
            >
              {t('FINISH')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
