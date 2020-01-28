import React, { useState } from 'react';
import moment from 'moment';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { Button, DialogActions } from '@material-ui/core';
import {
  useAllLocationsQuery,
  useCreateProgramMutation,
} from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid #e4e4e4;
  text-align: right;
`;

export function CreateProgram(): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const [mutate] = useCreateProgramMutation();
  const { data: locationsData } = useAllLocationsQuery();

  const submitFormHandler = async (values): Promise<void> => {
    const { id: locationId } = locationsData.allLocations.edges[0].node;
    const response = await mutate({
      variables: {
        programData: {
          ...values,
          startDate: moment(values.startDate).toISOString(),
          endDate: moment(values.endDate).toISOString(),
          locationId,
        },
      },
    });
    if (!response.errors && response.data.createProgram) {
      history.push(`/programs/${response.data.createProgram.program.id}`);
    }
  };

  const renderSubmit = (submit): React.ReactElement => {
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
    <div>
      <Button variant='contained' color='primary' onClick={() => setOpen(true)}>
        new programme
      </Button>

      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        open={open}
        onClose={() => setOpen(false)}
        title='Set-up a new Programme'
      />
    </div>
  );
}
