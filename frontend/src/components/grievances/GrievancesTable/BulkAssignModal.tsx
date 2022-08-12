import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '../../../containers/dialogs/Dialog';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  AllGrievanceTicketDocument,
  useBulkUpdateGrievanceAssigneeMutation,
} from '../../../__generated__/graphql';
import { AssignedToDropdown } from './AssignedToDropdown';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 400px;
  max-width: 800px;
`;
const StyledDialog = styled(Dialog)`
  max-height: 800px;
`;

const Bold = styled.span`
  font-weight: bold;
`;

interface BulkAssignModalProps {
  selected: string[];
  businessArea: string;
  optionsData;
  initialVariables;
  setInputValue;
  setSelected;
}

export const BulkAssignModal = ({
  selected,
  businessArea,
  optionsData,
  initialVariables,
  setInputValue,
  setSelected,
}: BulkAssignModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [assignee, setAssignee] = useState(null);
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();

  const [mutate] = useBulkUpdateGrievanceAssigneeMutation();

  const renderButton = (): React.ReactElement => {
    return (
      <Button
        variant='text'
        color='primary'
        disabled={!selected.length}
        onClick={() => setDialogOpen(true)}
      >
        {t('ASSIGN TICKETS')}
      </Button>
    );
  };

  const onSave = async (): Promise<void> => {
    if (assignee) {
      try {
        await mutate({
          variables: {
            assignedTo: assignee.node.id,
            businessAreaSlug: businessArea,
            grievanceTicketUnicefIds: selected,
          },
          refetchQueries: () => [
            {
              query: AllGrievanceTicketDocument,
              variables: { ...initialVariables },
            },
          ],
        });
      } catch (e) {
        e.graphQLErrors.map((x) => showMessage(x.message));
      } finally {
        setSelected([]);
      }
    }
  };

  const onFilterChange = (data): void => {
    if (data) {
      setAssignee(data);
    }
  };

  return (
    <>
      {renderButton()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Assign Ticket')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <StyledTable>
              <Typography>
                {t('Tickets ID')}:<Bold>{selected.join(', ')}</Bold>
              </Typography>
            </StyledTable>
          </Box>
          <StyledTable>
            <TableBody>
              <AssignedToDropdown
                optionsData={optionsData}
                onFilterChange={onFilterChange}
                setInputValue={setInputValue}
                label={t('Assignee')}
                fullWidth
              />
            </TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                setDialogOpen(false);
              }}
            >
              {t('CANCEL')}
            </Button>
            <Button
              variant='contained'
              color='primary'
              onClick={(e) => {
                e.stopPropagation();
                onSave();
                setDialogOpen(false);
              }}
            >
              {t('SAVE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </StyledDialog>
    </>
  );
};
