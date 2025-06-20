import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import { useSnackbar } from '@hooks/useSnackBar';
import { BulkBaseModal } from './BulkBaseModal';
import { ReactElement, useState } from 'react';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BulkUpdateGrievanceTicketsUrgency } from '@restgenerated/models/BulkUpdateGrievanceTicketsUrgency';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkSetUrgencyModalProps {
  selectedTickets: GrievanceTicketList[];
  setSelected;
}

export function BulkSetUrgencyModal({
  selectedTickets,
  setSelected,
}: BulkSetUrgencyModalProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessAreaSlug } = useBaseUrl();
  const [value, setValue] = useState<number>(0);
  const queryClient = useQueryClient();

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkUpdateGrievanceTicketsUrgency) => {
      return RestService.restBusinessAreasGrievanceTicketsBulkUpdateUrgencyCreate(
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
  const { data: choices } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug,
      }),
  });
  const urgencyChoices = choices.grievanceTicketUrgencyChoices;
  const onSave = async (): Promise<void> => {
    await mutateAsync({
      urgency: value,
      grievanceTicketIds: selectedTickets.map((ticket) => ticket.id),
    });
  };

  return (
    <BulkBaseModal
      selectedTickets={selectedTickets}
      title={t('Set Urgency')}
      buttonTitle={t('Set Urgency')}
      onSave={onSave}
      icon={<PriorityHighIcon />}
    >
      <FormControl variant="outlined" style={{ width: '100%' }}>
        <InputLabel id="urgency-label">{t('Urgency')}</InputLabel>
        <Select
          value={value}
          onChange={(e) => setValue(e.target.value as number)}
          label={t('Urgency')}
        >
          {urgencyChoices.map((choice) => (
            <MenuItem key={choice.value} value={choice.value}>
              {choice.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </BulkBaseModal>
  );
}
