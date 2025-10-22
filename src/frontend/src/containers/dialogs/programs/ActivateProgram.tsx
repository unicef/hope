import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();
  const queryClient = useQueryClient();

  const { mutateAsync: activateProgram, isPending: loading } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsActivateCreate({
        businessAreaSlug: businessArea,
        slug: program.slug,
      }),
    onSuccess: () => {
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatusEnum.ACTIVE,
      });
      showMessage(t('Programme activated.'));
      queryClient.invalidateQueries({
        queryKey: ['program', businessArea, program.slug],
      });
      setOpen(false);
    },
    onError: (error) => {
      showApiErrorMessages(
        error,
        showMessage,
        t('Programme activate action failed.'),
      );
    },
  });

  const handleActivateProgram = async(): Promise<void> => {
    await activateProgram();
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
              onClick={handleActivateProgram}
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
