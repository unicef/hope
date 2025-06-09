import { TextField } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import CommentIcon from '@mui/icons-material/Comment';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { BulkGrievanceTicketsAddNote } from '@restgenerated/models/BulkGrievanceTicketsAddNote';
import { BulkBaseModal } from './BulkBaseModal';
import { ReactElement, useState } from 'react';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkAddNoteModalProps {
  selectedTickets: GrievanceTicketList[];
  setSelected;
}

export function BulkAddNoteModal({
  selectedTickets,
  setSelected,
}: BulkAddNoteModalProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [value, setValue] = useState<string>('');
  const { businessAreaSlug } = useBaseUrl();
  const queryClient = useQueryClient();

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkGrievanceTicketsAddNote) => {
      return RestService.restBusinessAreasGrievanceTicketsBulkAddNoteCreate({
        businessAreaSlug,
        requestBody: params,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['businessAreasProgramsGrievanceTickets'],
      });
      queryClient.invalidateQueries({
        queryKey: ['businessAreasGrievanceTickets'],
      });
      setSelected([]);
    },
    onError: (error: any) => {
      const errorMessage =
        error?.body?.errors || error?.message || 'An error occurred';
      showMessage(errorMessage);
    },
  });

  const onSave = async (): Promise<void> => {
    try {
      await mutateAsync({
        grievanceTicketIds: selectedTickets.map((ticket) => ticket.id),
        note: value,
      });
    } catch (e) {
      // Error is handled in onError callback
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
