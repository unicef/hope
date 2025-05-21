import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import AlarmAddIcon from '@mui/icons-material/AlarmAdd';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBulkUpdateGrievancePriorityMutation } from '@generated/graphql';
import { BulkBaseModal } from './BulkBaseModal';
import { ReactElement, useState } from 'react';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkSetPriorityModalProps {
  selectedTickets: GrievanceTicketList[];
  businessArea: string;
  setSelected;
}

export const BulkSetPriorityModal = ({
  selectedTickets,
  businessArea,
  setSelected,
}: BulkSetPriorityModalProps): ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessAreaSlug } = useBaseUrl();
  const [value, setValue] = useState<number>(0);
  const [mutate] = useBulkUpdateGrievancePriorityMutation();

  const { data: choices } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug,
      }),
  });

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
      <FormControl variant="outlined" style={{ width: '100%' }}>
        <InputLabel>{t('Priority')}</InputLabel>
        <Select
          value={value}
          onChange={(e) => setValue(e.target.value as number)}
          label={t('Priority')}
        >
          {priorityChoices.map((choice) => (
            <MenuItem key={choice.value} value={choice.value}>
              {choice.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </BulkBaseModal>
  );
};
