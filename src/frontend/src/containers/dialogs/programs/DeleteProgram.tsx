import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import CloseIcon from '@mui/icons-material/CloseRounded';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllProgramsForChoicesDocument,
  ProgramQuery,
  useDeleteProgramMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useNavigate } from 'react-router-dom';

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
    min-width: ${({ theme }) => theme.spacing(120)};
  }
`;

interface DeleteProgramProps {
  program: ProgramQuery['program'];
}

export function DeleteProgram({
  program,
}: DeleteProgramProps): React.ReactElement {
  const navigate = useNavigate();
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
      showMessage(t('Programme removed'));
      navigate(`/${businessArea}/programs/all/list`);
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
}
