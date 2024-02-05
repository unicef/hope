import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import CloseIcon from '@material-ui/icons/CloseRounded';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllProgramsForChoicesDocument,
  ProgramQuery,
  useDeleteProgramMutation,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

const RemoveButton = styled(Button)`
  && {
    color: ${({ theme }) => theme.palette.error.main};
  }
`;

const RemoveModalButton = styled(Button)`
  && {
    background-color: ${({ theme }) => theme.palette.error.main};
  }
  &&:hover {
    background-color: ${({ theme }) => theme.palette.error.dark};
  }
`;
const MidDialog = styled(Dialog)`
  .MuiDialog-paperWidthSm {
    min-width: ${({ theme }) => theme.spacing(120)}px;
  }
`;

interface DeleteProgramProps {
  program: ProgramQuery['program'];
}

export const DeleteProgram = ({
  program,
}: DeleteProgramProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea } = useBaseUrl();
  const [mutate] = useDeleteProgramMutation();

  const deleteProgram = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          programId: program.id,
        },

        refetchQueries: () => [
          {
            query: AllProgramsForChoicesDocument,
            variables: { businessArea, first: 100 },
          },
        ],
      });
      showMessage(t('Programme removed'), {
        pathname: `/${businessArea}/programs/all/list`,
        historyMethod: 'push',
        dataCy: 'snackbar-program-remove-success',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <span>
      <RemoveButton
        startIcon={<CloseIcon />}
        onClick={() => setOpen(true)}
        data-cy="button-remove-program"
      >
        {t('REMOVE')}
      </RemoveButton>
      <MidDialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Remove Programme')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to remove this Programme?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-cancel" onClick={() => setOpen(false)}>
              {t('CANCEL')}
            </Button>
            <RemoveModalButton
              type="submit"
              color="primary"
              variant="contained"
              onClick={deleteProgram}
              data-cy="button-remove-program"
            >
              {t('REMOVE')}
            </RemoveModalButton>
          </DialogActions>
        </DialogFooter>
      </MidDialog>
    </span>
  );
};
