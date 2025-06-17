import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMutation } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
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
  const { baseUrl, businessAreaSlug } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();

  const { mutate, isPending: loading } = useMutation({
    mutationFn: async (programData: any) =>
      RestService.restBusinessAreasProgramsUpdate({
        businessAreaSlug,
        slug: program.id,
        requestBody: programData,
      }),
    onSuccess: () => {
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatus.ACTIVE,
      });
      showMessage(t('Programme reactivated.'));
      navigate(`/${baseUrl}/details/${program.id}`);
      setOpen(false);
    },
    onError: () => {
      showMessage(t('Programme reactivate action failed.'));
    },
  });

  const reactivateProgram = (): void => {
    mutate({
      ...program,
      status: ProgramStatus.ACTIVE,
    });
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
