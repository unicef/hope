import React, { useState } from 'react';
import moment from 'moment';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  Button,
  DialogActions,
  Snackbar,
  SnackbarContent,
} from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import {
  ProgramNode,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { PROGRAM_QUERY } from '../../../apollo/queries/Program';
import { useSnackbarHelper } from '../../../hooks/useBreadcrumbHelper';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/AllLogEntries';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

interface EditProgramProps {
  program: ProgramNode;
}

export function EditProgram({ program }: EditProgramProps): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const snackBar = useSnackbarHelper();
  const [mutate] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: program.id,
          count: 5,
        },
      },
    ],
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
  const businessArea = useBusinessArea();

  const submitFormHandler = async (values): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          ...values,
          startDate: moment(values.startDate).format('YYYY-MM-DD'),
          endDate: moment(values.endDate).format('YYYY-MM-DD'),
          budget: parseFloat(values.budget).toFixed(2),
        },
      },
    });
    if (!response.errors && response.data.updateProgram) {
      history.replace({
        pathname: `/${businessArea}/programs/${response.data.updateProgram.program.id}`,
        state: { showSnackbar: true, message: 'Programme edited.' },
      });
      setOpen(false);
    } else {
      history.replace({
        pathname: history.location.pathname,
        state: {showSnackbar: true, message: 'Programme edit action failed.'}
      })
    }
  };

  const renderSubmit = (submit): React.ReactElement => {
    return (
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
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
        title='Edit Programme Details'
      />
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={2000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent message={snackBar.message} />
        </Snackbar>
      )}
    </span>
  );
}
