import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { Status791Enum as ProgramStatus } from '@restgenerated/models/Status791Enum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from '../../../programContext';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

interface ReactivateProgramProps {
  program: ProgramDetail;
}

export function ReactivateProgram({
  program,
}: ReactivateProgramProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessAreaSlug } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();
  const queryClient = useQueryClient();

  const { mutate, isPending: loading } = useMutation({
    mutationFn: async () =>
      RestService.restBusinessAreasProgramsActivateCreate({
        businessAreaSlug,
        slug: program.slug,
      }),
    onSuccess: () => {
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatus.ACTIVE,
      });
      queryClient.invalidateQueries({
        queryKey: ['program', businessAreaSlug, program.slug],
      });
      showMessage(t('Programme reactivated.'));
      setOpen(false);
    },
    onError: () => {
      showMessage(t('Programme reactivate action failed.'));
    },
  });

  const reactivateProgram = (): void => {
    mutate();
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
