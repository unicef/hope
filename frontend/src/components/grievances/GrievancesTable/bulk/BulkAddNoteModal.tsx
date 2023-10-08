import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
  Table,
  TableBody,
  TextareaAutosize,
  TextField,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '../../../../containers/dialogs/Dialog';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  AllGrievanceTicketDocument,
  AllGrievanceTicketQuery,
  useBulkUpdateGrievanceAddNoteMutation,
  useBulkUpdateGrievanceAssigneeMutation,
  useBulkUpdateGrievancePriorityMutation,
  useGrievancesChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { AssignedToDropdown } from '../AssignedToDropdown';
import CommentIcon from '@material-ui/icons/Comment';
import { BulkBaseModal } from './BulkBaseModal';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkAddNoteModalProps {
  selectedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][];
  businessArea: string;
  setSelected;
}

export const BulkAddNoteModal = ({
  selectedTickets,
  businessArea,
  setSelected,
}: BulkAddNoteModalProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [value, setValue] = React.useState<string>('');
  const [mutate] = useBulkUpdateGrievanceAddNoteMutation();
  const onSave = async (
    tickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][],
  ): Promise<void> => {
    try {
      await mutate({
        variables: {
          note: value,
          businessAreaSlug: businessArea,
          grievanceTicketIds: selectedTickets.map((ticket) => ticket.id),
        },
        refetchQueries: ['AllGrievanceTicket'],
        awaitRefetchQueries: true,
      });
      setSelected([]);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
      throw e;
    }
  };

  return (
    <>
      <BulkBaseModal
        selectedTickets={selectedTickets}
        title={t('Add Note')}
        buttonTitle={t('add note')}
        onSave={onSave}
        icon={<CommentIcon />}
        disabledSave={!value}
      >
        <TextField
          variant='outlined'
          fullWidth
          value={value}
          onChange={(e) => setValue(e.target.value)}
          margin='dense'
        />
      </BulkBaseModal>
    </>
  );
};
