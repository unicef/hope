import React, { useState } from 'react';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import CloseIcon from '@material-ui/icons/CloseRounded';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import {
  AllProgramsQuery,
  ProgramNode,
  useDeleteProgramMutation,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/AllPrograms';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: ${({ theme }) => theme.spacing(5)}px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;
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
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const businessArea = useBusinessArea();
  const [mutate] = useDeleteProgramMutation({
    variables: {
      programId: program.id,
    },
  });
  const deleteProgram = async (): Promise<void> => {
    await mutate({
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
    history.push(`/${businessArea}/programs/`);
    setOpen(false);
  };
  return (
    <span>
      <RemoveButton startIcon={<CloseIcon />} onClick={() => setOpen(true)}>
        REMOVE
      </RemoveButton>
      <MidDialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Remove Programme</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            Are you sure you want to remove this Programme?
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)} >
              CANCEL
            </Button>
            <RemoveModalButton
              type='submit'
              color='primary'
              variant='contained'
              onClick={deleteProgram}
            >
              REMOVE
            </RemoveModalButton>
          </DialogActions>
        </DialogFooter>
      </MidDialog>
    </span>
  );
}
