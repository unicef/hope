import { LoadingButton } from '@components/core/LoadingButton';
import { useUpdateProgramMutation } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { Status791Enum as ProgramStatus } from '@restgenerated/models/Status791Enum';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from '../../../programContext';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

interface ActivateProgramProps {
  program: ProgramDetail;
}

export const ActivateProgram = ({
  program,
}: ActivateProgramProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();

  const [mutate, { loading }] = useUpdateProgramMutation();

  const activateProgram = async (): Promise<void> => {
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

      showMessage(t('Programme activated.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
      setOpen(false);
    } else {
      showMessage(t('Programme activate action failed.'));
    }
  };
  return (
    <span>
      <Button
        variant="contained"
        color="primary"
        onClick={() => setOpen(true)}
        data-cy="button-activate-program"
      >
        Activate
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Activate Programme')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to activate this Programme?')}
            <br />
            {t(
              'Upon activation of this Programme, default Programme Cycles will be created.',
            )}
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
              onClick={activateProgram}
              data-cy="button-activate-program-modal"
            >
              {t('ACTIVATE')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
};
