import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllProgramsQuery,
  ProgramNode,
  ProgramStatus,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { GreyText } from '../../../components/core/GreyText';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { programCompare } from '../../../utils/utils';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

const WhiteDeleteIcon = styled(Delete)`
  color: #fff;
`;

interface RemoveProgramCycleProps {
  program: ProgramNode;
  canRemoveProgramCycle: boolean;
}

export const RemoveProgramCycle = ({
  program,
  canRemoveProgramCycle,
}: RemoveProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();

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

  const save = async (): Promise<void> => {
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
        pathname: `/${baseUrl}/details/${response.data.updateProgram.program.id}`,
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
    <>
      <IconButton
        onClick={() => {
          setOpen(true);
        }}
        disabled={!canRemoveProgramCycle}
        color='primary'
      >
        <Delete />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
        <DialogTitleWrapper>
          <DialogTitle>
            {t(
              'Are you sure you want to delete the Program Cycle from the system?',
            )}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <GreyText>{t('This action cannot be undone.')}</GreyText>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={loading}
              error
              type='submit'
              variant='contained'
              onClick={save}
              data-cy='button-delete'
              endIcon={<WhiteDeleteIcon />}
            >
              {t('Delete Program Cycle')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
