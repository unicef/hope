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
import { useCreateProgramMutation } from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbarHelper } from '../../../hooks/useBreadcrumbHelper';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

export function CreateProgram(): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const snackBar = useSnackbarHelper();
  const [mutate] = useCreateProgramMutation();
  const businessArea = useBusinessArea();

  const submitFormHandler = async (values): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          ...values,
          startDate: moment(values.startDate).format('YYYY-MM-DD'),
          endDate: moment(values.endDate).format('YYYY-MM-DD'),
          businessAreaSlug: businessArea,
        },
      },
    });
    if (!response.errors && response.data.createProgram) {
      history.push({
        pathname: `/${businessArea}/programs/${response.data.createProgram.program.id}`,
        state: { showSnackbar: true, message: 'Programme created.' },
      });
    } else {
      history.replace({
        pathname: history.location.pathname,
        state: {showSnackbar: true, message: 'Programme create action failed.'}
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
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={2000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent message={snackBar.message} />
        </Snackbar>
      )}
    </div>
  );
}
