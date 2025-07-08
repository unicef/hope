import { deleteProgramCycle, ProgramCycle } from '@api/programCycleApi';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { GreyText } from '@core/GreyText';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import DeleteIcon from '@mui/icons-material/Delete';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { decodeIdString, showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const WhiteDeleteIcon = styled(DeleteIcon)`
  color: #fff;
`;

interface DeleteProgramCycleProps {
  program: ProgramDetail;
  programCycle: ProgramCycle;
}

const DeleteProgramCycle = ({
  program,
  programCycle,
}: DeleteProgramCycleProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn: async () => {
      return deleteProgramCycle(
        businessArea,
        program.id,
        decodeIdString(programCycle.id),
      );
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programCycles', businessArea, program.id],
      });
      setOpen(false);
    },
  });

  const handleDelete = async (): Promise<void> => {
    try {
      await mutateAsync();
      showMessage(t('Programme Cycle Deleted'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <>
      <IconButton
        color="primary"
        data-cy="delete-programme-cycle"
        onClick={() => setOpen(true)}
      >
        <DeleteIcon />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <DialogTitleWrapper>
          <DialogTitle>
            {
              'Are you sure you want to delete the Program Cycle from the system?'
            }
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <GreyText>{t('This action cannot be undone.')}</GreyText>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={isPending}
              color="error"
              variant="contained"
              onClick={handleDelete}
              data-cy="button-delete"
              endIcon={<WhiteDeleteIcon />}
            >
              {t('Delete')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};

export default withErrorBoundary(DeleteProgramCycle, 'DeleteProgramCycle');
