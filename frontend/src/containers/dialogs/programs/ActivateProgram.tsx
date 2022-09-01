import {
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { programCompare } from '../../../utils/utils';
import {
  AllProgramsQuery,
  ProgramNode,
  ProgramStatus,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

interface ActivateProgramProps {
  program: ProgramNode;
}

export function ActivateProgram({
  program,
}: ActivateProgramProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, { loading }] = useUpdateProgramMutation({
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
      const allProgramsData: AllProgramsQuery = cache.readQuery({
        query: ALL_PROGRAMS_QUERY,
        variables: { businessArea },
      });
      allProgramsData.allPrograms.edges.sort(programCompare);
      cache.writeQuery({
        query: ALL_PROGRAMS_QUERY,
        variables: { businessArea },
        data: allProgramsData,
      });
    },
  });
  const activateProgram = async (): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          status: ProgramStatus.Active,
        },
        version: program.version,
      },
    });
    if (!response.errors && response.data.updateProgram) {
      showMessage(t('Programme activated.'), {
        pathname: `/${businessArea}/programs/${response.data.updateProgram.program.id}`,
        dataCy: 'snackbar-program-activate-success',
      });
      setOpen(false);
    } else {
      showMessage(t('Programme activate action failed.'), {
        dataCy: 'snackbar-program-activate-failure',
      });
    }
  };
  return (
    <span>
      <Button
        variant='contained'
        color='primary'
        onClick={() => setOpen(true)}
        data-cy='button-activate-program'
      >
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
            <Typography variant='h6'>{t('Activate Programme')}</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to activate this Programme?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={loading}
              type='submit'
              color='primary'
              variant='contained'
              onClick={activateProgram}
              data-cy='button-activate-program-modal'
            >
              {t('ACTIVATE')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
