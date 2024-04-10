import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsQuery,
  ProgramQuery,
  ProgramStatus,
  useUpdateProgramMutation,
} from '@generated/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { programCompare } from '@utils/utils';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useProgramContext } from '../../../programContext';
import { useNavigate } from 'react-router-dom';

interface ActivateProgramProps {
  program: ProgramQuery['program'];
}

export const ActivateProgram = ({
  program,
}: ActivateProgramProps): React.ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();

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

      if (allProgramsData && allProgramsData.allPrograms) {
        allProgramsData.allPrograms.edges.sort(programCompare);
        cache.writeQuery({
          query: ALL_PROGRAMS_QUERY,
          variables: { businessArea },
          data: allProgramsData,
        });
      }
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
      setSelectedProgram({
        ...selectedProgram,
        status: ProgramStatus.Active,
      });

      showMessage(t('Programme activated.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
      setOpen(false);
    } else {
      showMessage(t('Programme activate action failed.'));
    }
  };
  return (
    <span>
      <Button
        variant="contained"
        color="primary"
        onClick={() => setOpen(true)}
        data-cy="button-activate-program"
      >
        Activate
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Activate Programme')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to activate this Programme?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-cancel" onClick={() => setOpen(false)}>
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={loading}
              type="submit"
              color="primary"
              variant="contained"
              onClick={activateProgram}
              data-cy="button-activate-program-modal"
            >
              {t('ACTIVATE')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
};
