import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { BulkUpdateGrievanceTicketsUrgency } from '@restgenerated/models/BulkUpdateGrievanceTicketsUrgency';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BulkBaseModal } from './BulkBaseModal';

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
  const { businessAreaSlug, isAllPrograms, programId } = useBaseUrl();
  const [value, setValue] = useState<number>(0);
  const queryClient = useQueryClient();

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkUpdateGrievanceTicketsUrgency) => {
      return RestService.restBusinessAreasGrievanceTicketsBulkUpdateUrgencyCreate(
        {
          businessAreaSlug,
          formData: params,
        },
      );
    },
    onSuccess: () => {
      if (isAllPrograms) {
        queryClient.invalidateQueries({
          queryKey: ['businessAreasGrievanceTickets'],
        });
      } else {
        queryClient.invalidateQueries({
          queryKey: [
            'businessAreasProgramsGrievanceTickets',
            { program: programId },
          ],
        });
      }
      setSelected([]);
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
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
          onChange={(e) => setValue(e.target.value)}
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
