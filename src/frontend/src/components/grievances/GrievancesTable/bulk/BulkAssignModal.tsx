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
import { restQueryKey } from '@utils/queryKeys';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BulkUpdateGrievanceTicketsAssignees } from '@restgenerated/models/BulkUpdateGrievanceTicketsAssignees';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ApiErrorShape, showApiErrorMessages } from '@utils/utils';

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
  const { businessAreaSlug, isAllPrograms } = useBaseUrl();
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
          queryKey: restQueryKey(
            RestService.restBusinessAreasGrievanceTicketsList,
          ),
        });
      } else {
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsGrievanceTicketsList,
          ),
        });
      }
      setSelected([]);
    },
    onError: (error: ApiErrorShape) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  // `satisfies` keeps the orderBy string literals narrowed to the fetcher's enum, which a
  // bare object literal loses once it is hoisted out of the call.
  const usersParams = {
    businessAreaSlug: businessAreaSlug,
    limit: 20,
    orderBy: ['first_name', 'last_name', 'email'],
    search: inputValue,
  } satisfies Parameters<typeof RestService.restBusinessAreasUsersList>[0];
  const { data: usersData } = useQuery({
    queryKey: restQueryKey(RestService.restBusinessAreasUsersList, usersParams),
    queryFn: () => RestService.restBusinessAreasUsersList(usersParams),
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
