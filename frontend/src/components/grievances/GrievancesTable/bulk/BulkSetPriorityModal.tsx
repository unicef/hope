import { MenuItem, Select } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import AlarmAddIcon from '@mui/icons-material/AlarmAdd';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  AllGrievanceTicketQuery,
  useBulkUpdateGrievancePriorityMutation,
  useGrievancesChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { BulkBaseModal } from './BulkBaseModal';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkSetPriorityModalProps {
  selectedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][];
  businessArea: string;
  setSelected;
}

export function BulkSetPriorityModal({
  selectedTickets,
  businessArea,
  setSelected,
}: BulkSetPriorityModalProps): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [value, setValue] = React.useState<number>(0);
  const [mutate] = useBulkUpdateGrievancePriorityMutation();
  const { data: choices } = useGrievancesChoiceDataQuery();
  const priorityChoices = choices.grievanceTicketPriorityChoices;
  const onSave = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          priority: value,
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
      title={t('Set priority')}
      buttonTitle={t('Set priority')}
      onSave={onSave}
      icon={<AlarmAddIcon />}
    >
      <Select
        value={value}
        onChange={(e) => setValue(e.target.value as number)}
        style={{ width: '100%' }}
        variant="outlined"
        margin="dense"
        label={t('Priority')}
      >
        {priorityChoices.map((choice) => (
          <MenuItem key={choice.value} value={choice.value}>
            {choice.name}
          </MenuItem>
        ))}
      </Select>
    </BulkBaseModal>
  );
}
