import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import {
  ProgramNode,
  ProgramStatus,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { PROGRAM_QUERY } from '../../../apollo/queries/Program';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({theme})=>theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({theme})=>theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

interface ActivateProgramProps {
  program: ProgramNode;
}

export function ActivateProgram({
  program,
}: ActivateProgramProps): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [mutate] = useUpdateProgramMutation({
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
    },
  });
  const activateProgram = async (): Promise<void> => {
    await mutate({
      variables: {
        programData: {
          id: program.id,
          status: ProgramStatus.Active,
        },
      },
    });
    setOpen(false);
  };
  return (
    <span>
      <Button variant='contained' color='primary' onClick={() => setOpen(true)}>
        Activate
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Activate Programme</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            Are you sure you want to activate this Programme and push data to
            CashAssist?
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)} color='primary'>
              CANCEL
            </Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={activateProgram}
            >
              ACTIVATE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
