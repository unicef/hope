import { TextField } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import CommentIcon from '@mui/icons-material/Comment';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  AllGrievanceTicketQuery,
  useBulkUpdateGrievanceAddNoteMutation,
} from '@generated/graphql';
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

export function BulkAddNoteModal({
  selectedTickets,
  businessArea,
  setSelected,
}: BulkAddNoteModalProps): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [value, setValue] = React.useState<string>('');
  const [mutate] = useBulkUpdateGrievanceAddNoteMutation();
  const onSave = async (): Promise<void> => {
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
    <BulkBaseModal
      selectedTickets={selectedTickets}
      title={t('Add Note')}
      buttonTitle={t('add note')}
      onSave={onSave}
      icon={<CommentIcon />}
      disabledSave={!value}
    >
      <TextField
        variant="outlined"
        label={t('Note')}
        fullWidth
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </BulkBaseModal>
  );
}
