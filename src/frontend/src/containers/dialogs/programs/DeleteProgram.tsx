import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import CloseIcon from '@mui/icons-material/CloseRounded';
import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

const RemoveButton = styled(Button)`
  && {
    color: ${({ theme }) => theme.palette.error.main};
  }
`;

const RemoveModalButton = styled(Button)`
  && {
    background-color: ${({ theme }) => theme.palette.error.main};
  }
  &&:hover {
    background-color: ${({ theme }) => theme.palette.error.dark};
  }
`;
const MidDialog = styled(Dialog)`
  .MuiDialog-paperWidthSm {
    min-width: ${({ theme }) => theme.spacing(120)};
  }
`;

interface DeleteProgramProps {
  program: ProgramDetail;
}

export const DeleteProgram = ({
  program,
}: DeleteProgramProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const { mutateAsync: deleteProgram, isPending: isPendingDelete } =
    useMutation({
      mutationFn: () =>
        RestService.restBusinessAreasProgramsDestroy({
          businessAreaSlug: businessArea,
          slug: program.slug,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: ['businessAreasProgramsList', businessArea, programId],
        });
        showMessage(t('Programme removed'));
        navigate(`/${businessArea}/programs/all/list`);
      },
      onError: (e) => {
        // Handle empty response error as success
        if (e.message && e.message.includes('Unexpected end of JSON input')) {
          showMessage(t('Programme removed'));
          navigate(`/${businessArea}/programs/all/list`);
        } else {
          showMessage(e.message);
        }
      },
    });

  return (
    <span>
      <RemoveButton
        startIcon={<CloseIcon />}
        onClick={() => setOpen(true)}
        data-cy="button-remove-program"
      >
        {t('REMOVE')}
      </RemoveButton>
      <MidDialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Remove Programme')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to remove this Programme?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-cancel" onClick={() => setOpen(false)}>
              {t('CANCEL')}
            </Button>
            <RemoveModalButton
              type="submit"
              color="primary"
              variant="contained"
              disabled={isPendingDelete}
              onClick={() => deleteProgram()}
              data-cy="button-remove-program"
            >
              {t('REMOVE')}
            </RemoveModalButton>
          </DialogActions>
        </DialogFooter>
      </MidDialog>
    </span>
  );
};
