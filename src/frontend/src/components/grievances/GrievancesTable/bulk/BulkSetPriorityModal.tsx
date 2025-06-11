import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import AlarmAddIcon from '@mui/icons-material/AlarmAdd';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { BulkUpdateGrievanceTicketsPriority } from '@restgenerated/models/BulkUpdateGrievanceTicketsPriority';
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

interface BulkSetPriorityModalProps {
  selectedTickets: GrievanceTicketList[];
  setSelected;
}

export const BulkSetPriorityModal = ({
  selectedTickets,
  setSelected,
}: BulkSetPriorityModalProps): ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessAreaSlug } = useBaseUrl();
  const [value, setValue] = useState<number>(0);
  const queryClient = useQueryClient();

  const { data: choices } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug,
      }),
  });

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkUpdateGrievanceTicketsPriority) => {
      return RestService.restBusinessAreasGrievanceTicketsBulkUpdatePriorityCreate(
        {
          businessAreaSlug,
          requestBody: params,
        },
      );
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

  const priorityChoices = choices?.grievanceTicketPriorityChoices;
  const onSave = async (): Promise<void> => {
    await mutateAsync({
      grievanceTicketIds: selectedTickets.map((ticket) => ticket.id),
      priority: value,
    });
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
          {priorityChoices?.map((choice) => (
            <MenuItem key={choice.value} value={choice.value}>
              {choice.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </BulkBaseModal>
  );
};
