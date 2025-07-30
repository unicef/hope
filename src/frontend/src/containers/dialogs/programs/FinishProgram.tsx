import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useProgramContext } from '../../../programContext';
import { useNavigate } from 'react-router-dom';
import { ProgramStatusEnum} from '@restgenerated/models/ProgramStatusEnum';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { showApiErrorMessages } from '@utils/utils';

interface FinishProgramProps {
  program: ProgramDetail;
}

export function FinishProgram({ program }: FinishProgramProps): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();

  const { mutateAsync: finishProgramMutation, isPending: loading } =
    useMutation({
      mutationFn: () =>
        RestService.restBusinessAreasProgramsFinishCreate({
          businessAreaSlug: businessArea,
          slug: program.slug,
        }),
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: ['program', businessArea, program.slug],
        });
      },
    });

  const finishProgram = async (): Promise<void> => {
    try {
      await finishProgramMutation();
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatusEnum.FINISHED,
      });
      showMessage(t('Programme finished.'));
      navigate(`/${baseUrl}/details/${program.slug}`);
      setOpen(false);
    } catch (error: any) {
      showApiErrorMessages(
        error,
        showMessage,
        t('Failed to finish programme.'),
      );
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
