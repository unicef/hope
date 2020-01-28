import React, { useState } from 'react';
import moment from 'moment';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { Button, Dialog, DialogActions } from '@material-ui/core';
import {
  ProgramNode,
  useAllLocationsQuery,
  useCreateProgramMutation,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';
import EditIcon from '@material-ui/icons/EditRounded';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid #e4e4e4;
  text-align: right;
`;

interface EditProgramProps {
  program: ProgramNode;
}

export function EditProgram({ program }: EditProgramProps): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const [mutate] = useUpdateProgramMutation();

  const submitFormHandler = async (values) => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          ...values,
          startDate: moment(values.startDate).toISOString(),
          endDate: moment(values.endDate).toISOString(),
        },
      },
    });
    if (!response.errors && response.data.updateProgram) {
      history.push(`/programs/${response.data.updateProgram.program.id}`);
    }
    setOpen(false);
  };

  const renderSubmit = (submit) => {
    return (
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)} color='primary'>
            Cancel
          </Button>
          <Button
            onClick={submit}
            type='submit'
            color='primary'
            variant='contained'
          >
            Save
          </Button>
        </DialogActions>
      </DialogFooter>
    );
  };

  return (
    <span>
      <Button
        variant='outlined'
        color='primary'
        startIcon={<EditIcon />}
        onClick={() => setOpen(true)}
      >
        EDIT PROGRAMME
      </Button>
      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        program={program}
        open={open}
        onClose={() => setOpen(false)}
      />
    </span>
  );
}
