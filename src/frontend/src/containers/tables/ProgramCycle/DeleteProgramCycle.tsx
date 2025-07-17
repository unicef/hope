import { RestService } from '@restgenerated/services/RestService';
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
import { ProgramCycleCreate } from '@restgenerated/models/ProgramCycleCreate';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const WhiteDeleteIcon = styled(DeleteIcon)`
  color: #fff;
`;

interface DeleteProgramCycleProps {
  program: ProgramDetail;
  programCycle: ProgramCycleCreate;
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
    mutationFn: () => {
      // Use the generated RestService method for deleting a program cycle
      return RestService.restBusinessAreasProgramsCyclesDestroy({
        businessAreaSlug: businessArea,
        programSlug: program.slug,
        //@ts-ignore
        id: programCycle.id,
      });
    },
  });

  const handleDelete = async (): Promise<void> => {
    try {
      await mutateAsync();
      showMessage(t('Programme Cycle Deleted'));
    } catch (e) {
      // Ignore empty response error
      if (e.message && e.message.includes('Unexpected end of JSON input')) {
        showMessage(t('Programme Cycle Deleted'));
      } else {
        showApiErrorMessages(e, showMessage);
      }
    }
    await queryClient.invalidateQueries({
      queryKey: ['programCycles', businessArea, program.slug],
      exact: false,
    });
    setOpen(false);
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
