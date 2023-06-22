import { Button, Dialog, DialogContent, DialogTitle } from '@material-ui/core';
import CloseIcon from '@material-ui/icons/CloseRounded';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  AllProgramsQuery,
  ProgramNode,
  useDeleteProgramMutation,
} from '../../../__generated__/graphql';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

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
    min-width: ${({ theme }) => theme.spacing(120)}px;
  }
`;

interface DeleteProgramProps {
  program: ProgramNode;
}

export function DeleteProgram({
  program,
}: DeleteProgramProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const [mutate] = useDeleteProgramMutation({
    variables: {
      programId: program.id,
    },
  });
  const deleteProgram = async (): Promise<void> => {
    const response = await mutate({
      update(cache) {
        const allProgramsData = cache.readQuery<AllProgramsQuery>({
          query: ALL_PROGRAMS_QUERY,
          variables: { businessArea },
        });
        const filtred = allProgramsData.allPrograms.edges.filter((item) => {
          return item.node.id !== program.id;
        });
        const newAllProgramsData = { ...allProgramsData };
        newAllProgramsData.allPrograms.edges = filtred;
        cache.writeQuery({
          query: ALL_PROGRAMS_QUERY,
          variables: { businessArea },
          data: newAllProgramsData,
        });
      },
    });
    if (!response.errors && response.data.deleteProgram) {
      showMessage(t('Programme removed.'), {
        pathname: `/${baseUrl}/list`,
        historyMethod: 'push',
        dataCy: 'snackbar-program-remove-success',
      });
      setOpen(false);
    } else {
      showMessage(t('Programme remove action failed.'), {
        dataCy: 'snackbar-program-remove-failure',
      });
    }
  };
  return (
    <span>
      <RemoveButton
        startIcon={<CloseIcon />}
        onClick={() => setOpen(true)}
        data-cy='button-remove-program'
      >
        {t('REMOVE')}
      </RemoveButton>
      <MidDialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
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
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <RemoveModalButton
              type='submit'
              color='primary'
              variant='contained'
              onClick={deleteProgram}
              data-cy='button-remove-program'
            >
              {t('REMOVE')}
            </RemoveModalButton>
          </DialogActions>
        </DialogFooter>
      </MidDialog>
    </span>
  );
}
