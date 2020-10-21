import React from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
  makeStyles,
} from '@material-ui/core';
import styled from 'styled-components';
import WarningIcon from '@material-ui/icons/Warning';
import { Field, Formik } from 'formik';
import * as Yup from 'yup';
import { ProgrammeAutocomplete } from '../../../shared/ProgrammeAutocomplete';
import {
  useAllProgramsQuery,
  useApproveTpMutation,
} from '../../../__generated__/graphql';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { DialogActions } from '../DialogActions';
import { Dialog } from '../Dialog';
import { MiśTheme } from '../../../theme';

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

const Box = styled.div`
  display: flex;
  align-items: center;
`;

const validationSchema = Yup.object().shape({
  program: Yup.object().shape({
    id: Yup.string().required('Programme is required'),
  }),
});

const useStyles = makeStyles((theme: MiśTheme) => ({
  warning: { color: theme.hctPalette.oragne, marginRight: '10px' },
}));

export function ApproveCandidateList({
  open,
  setOpen,
  targetPopulationId,
}): React.ReactElement {
  const businessArea = useBusinessArea();
  const { data: programs } = useAllProgramsQuery({
    variables: { status: ['ACTIVE'], businessArea },
  });
  const { showMessage } = useSnackbar();
  const [mutate, loading] = useApproveTpMutation();
  const classes = useStyles();
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
        initialValues={{ program: null }}
        onSubmit={(values) => {
          mutate({
            variables: { id: targetPopulationId},
          }).then(() => {
            setOpen(false);
            showMessage('Programme Population Approved', {
              pathname: `/${businessArea}/target-population/${targetPopulationId}`,
            });
          });
        }}
      >
        {({ submitForm, values, setFieldValue }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>Close Programme Population</Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                After you close this Programme Population, the selected criteria
                will no longer accept new results from the Population. Only the
                Target Population can be editable.
              </DialogDescription>
              <DialogDescription>
                Note: You may duplicate the Programme Population target criteria
                at any time.
              </DialogDescription>
              <DialogDescription>
                Please select a Programme that this list will be associated
                with.
              </DialogDescription>
              <DialogDescription>
                <Box>
                  <WarningIcon className={classes.warning} />
                  You can only select a programme that is compatible with your
                  filtering criteria
                </Box>
              </DialogDescription>
              {values.program && values.program.individualDataNeeded ? (
                <DialogDescription>
                  <strong>
                    Warning: You can only select a programme that is compatible
                    with your filtering criteria
                  </strong>
                </DialogDescription>
              ) : null}

              <Field
                name='program'
                label='Select a Programme'
                choices={choices}
                getOptionDisabled={(option) => {
                  if (option.status === 'ACTIVE') {
                    return false;
                  }
                  return true;
                }}
                onChange={(e, object) => {
                  if (object) {
                    setFieldValue('program', object);
                  }
                }}
                component={ProgrammeAutocomplete}
              />
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  disabled={
                    !loading ||
                    !values.program ||
                    values.program.status !== 'ACTIVE'
                  }
                  data-cy='button-target-population-close'
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
