import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { Formik } from 'formik';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDeleteTargetPopulationMutation } from '../../../__generated__/graphql';

export interface DeleteTargetPopulation {
  open: boolean;
  setOpen: Function;
}

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

export function DeleteTargetPopulation({ open, setOpen, targetPopulationId }) {
  const [mutate] = useDeleteTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const initialValues = {
    id: targetPopulationId,
  };
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <Formik
        validationSchema={null}
        initialValues={initialValues}
        onSubmit={async (values) => {
          const { data } = await mutate({
            variables: {input: {targetId: targetPopulationId}},
          });
          setOpen(false);
          showMessage('Target Population Deleted', {
            pathname: `/${businessArea}/target-population/`,
            historyMethod: 'push',
          });
        }}
      >
        {({ submitForm }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>Delete Target Population</Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                Are you sure you want to delete this Target Population?
              </DialogDescription>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <Button type='submit' color='primary' variant='contained' onClick={submitForm}>
                  Delete
                </Button>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
}
