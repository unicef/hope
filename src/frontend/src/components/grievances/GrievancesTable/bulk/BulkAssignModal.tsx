import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import { useSnackbar } from '@hooks/useSnackBar';
import { AssignedToDropdown } from '../AssignedToDropdown';
import { BulkBaseModal } from './BulkBaseModal';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { User } from '@restgenerated/models/User';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BulkUpdateGrievanceTicketsAssignees } from '@restgenerated/models/BulkUpdateGrievanceTicketsAssignees';
import { useBaseUrl } from '@hooks/useBaseUrl';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkAssignModalProps {
  selectedTickets: GrievanceTicketList[];
  setSelected;
}

export function BulkAssignModal({
  selectedTickets,
  setSelected,
}: BulkAssignModalProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessAreaSlug, isAllPrograms, programId } = useBaseUrl();
  const [value, setValue] = useState<User | null>(null);
  const [inputValue, setInputValue] = useState('');
  const queryClient = useQueryClient();

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkUpdateGrievanceTicketsAssignees) => {
      return RestService.restBusinessAreasGrievanceTicketsBulkUpdateAssigneeCreate(
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
      const errorMessage =
        error?.body?.errors || error?.message || 'An error occurred';
      showMessage(errorMessage);
    },
  });

  const { data: usersData } = useQuery({
    queryKey: ['users', businessAreaSlug, inputValue],
    queryFn: () =>
      RestService.restBusinessAreasUsersList({
        businessAreaSlug: businessAreaSlug,
        limit: 20,
        orderBy: ['first_name', 'last_name', 'email'],
        search: inputValue,
      }),
  });

  const optionsData: User[] = usersData?.results || [];

  const onFilterChange = (data: User | null): void => {
    setValue(data);
  };
  const onSave = async (): Promise<void> => {
    await mutateAsync({
      assignedTo: value?.id || '',
      grievanceTicketIds: selectedTickets.map((ticket) => ticket.id),
    });
  };

  return (
    <BulkBaseModal
      selectedTickets={selectedTickets}
      title={t('Assign')}
      buttonTitle={t('Assign')}
      onSave={onSave}
      icon={<AssignmentIndIcon />}
    >
      <AssignedToDropdown
        optionsData={optionsData}
        onFilterChange={onFilterChange}
        setInputValue={setInputValue}
        label={t('Assignee')}
        fullWidth
      />
    </BulkBaseModal>
  );
}
