import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBulkUpdateGrievanceAssigneeMutation } from '@generated/graphql';
import { AssignedToDropdown } from '../AssignedToDropdown';
import { BulkBaseModal } from './BulkBaseModal';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { User } from '@restgenerated/models/User';
import { PaginatedUserList } from '@restgenerated/models/PaginatedUserList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface BulkAssignModalProps {
  selectedTickets: GrievanceTicketList[];
  businessArea: string;
  setSelected;
}

export function BulkAssignModal({
  selectedTickets,
  businessArea,
  setSelected,
}: BulkAssignModalProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [value, setValue] = useState<User | null>(null);
  const [mutate] = useBulkUpdateGrievanceAssigneeMutation();
  const [inputValue, setInputValue] = useState('');

  const { data: usersData } = useQuery({
    queryKey: ['users', businessArea, inputValue],
    queryFn: () =>
      RestService.restBusinessAreasUsersList({
        businessAreaSlug: businessArea,
        limit: 20,
        orderBy: ['first_name', 'last_name', 'email'],
        search: inputValue,
      }),
  });

  const optionsData: PaginatedUserList = usersData || { results: [] };

  const onFilterChange = (data: User | null): void => {
    setValue(data);
  };
  const onSave = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          assignedTo: value?.id,
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
