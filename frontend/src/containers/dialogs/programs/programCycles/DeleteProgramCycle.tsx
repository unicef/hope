import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useDeleteProgramCycleMutation } from '../../../../__generated__/graphql';
import { ALL_PROGRAM_CYCLES_QUERY } from '../../../../apollo/queries/program/programcycles/AllProgramCycles';
import { GreyText } from '../../../../components/core/GreyText';
import { LoadingButton } from '../../../../components/core/LoadingButton';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { DialogDescription } from '../../DialogDescription';
import { DialogFooter } from '../../DialogFooter';
import { DialogTitleWrapper } from '../../DialogTitleWrapper';

const WhiteDeleteIcon = styled(Delete)`
  color: #fff;
`;

interface DeleteProgramCycleProps {
  programCycle;
  canDeleteProgramCycle: boolean;
}

export const DeleteProgramCycle = ({
  programCycle,
  canDeleteProgramCycle,
}: DeleteProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();

  const [mutate, { loading }] = useDeleteProgramCycleMutation();

  const handleDelete = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          programCycleId: programCycle.id,
        },
        refetchQueries: () => [{ query: ALL_PROGRAM_CYCLES_QUERY }],
        awaitRefetchQueries: true,
      });
      showMessage('Programme Cycle deleted.');
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <>
      <IconButton
        onClick={() => {
          setOpen(true);
        }}
        disabled={!canDeleteProgramCycle}
        color='primary'
      >
        <Delete />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
        <DialogTitleWrapper>
          <DialogTitle>
            {`Are you sure you want to delete the Program Cycle ${programCycle.id} from the system?`}
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
              loading={loading}
              error
              type='submit'
              variant='contained'
              onClick={handleDelete}
              data-cy='button-delete'
              endIcon={<WhiteDeleteIcon />}
            >
              {t('Delete Program Cycle')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
