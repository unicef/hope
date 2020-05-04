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
import { Field, Formik } from 'formik';
import * as Yup from 'yup';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import {
  useAllProgramsQuery,
  useApproveTpMutation,
} from '../../../__generated__/graphql';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

export interface ApproveCandidateListPropTypes {
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

const validationSchema = Yup.object().shape({
  program: Yup.string().required('Programme is required'),
});

export function ApproveCandidateList({ open, setOpen, targetPopulationId }) {
  const { data: programs } = useAllProgramsQuery();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, loading] = useApproveTpMutation();
  if (!programs) return null;
  const choices = programs.allPrograms.edges.map((program) => {
    return { ...program.node, value: program.node.id };
  });
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <Formik
        validationSchema={validationSchema}
        initialValues={{ program: '' }}
        onSubmit={(values) => {
          mutate({
            variables: { id: targetPopulationId, programId: values.program },
          }).then(() => {
            setOpen(false);
            showMessage('Candidate List Approved', {
              pathname: `/${businessArea}/target-population/${targetPopulationId}`,
            });
          });
        }}
      >
        {({ submitForm, values }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>Close Candidate List</Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                Are you sure you want to approve the targeting criteria for this
                Candidate List? Once a Candidate List is{' '}
                <strong>Approved</strong> the targeting criteria will be
                permanently frozen.
              </DialogDescription>
              <DialogDescription>
                Note: You may duplicate tthe Programme Population target criteria at any time.
              </DialogDescription>
              <DialogDescription>
                Please select a Programme you would like to associate this
                candidate list with:
              </DialogDescription>
              <Field
                name='program'
                label='Programme'
                choices={choices}
                component={FormikSelectField}
              />
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <Button
                  type="submit"
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  disabled={!loading || !values.program}
                >
                  Close
                </Button>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
}
