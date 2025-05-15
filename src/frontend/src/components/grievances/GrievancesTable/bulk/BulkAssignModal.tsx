import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  AllUsersForFiltersQuery,
  useAllUsersForFiltersQuery,
  useBulkUpdateGrievanceAssigneeMutation,
} from '@generated/graphql';
import { AssignedToDropdown } from '../AssignedToDropdown';
import { BulkBaseModal } from './BulkBaseModal';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';

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
  const [value, setValue] =
    useState<AllUsersForFiltersQuery['allUsers']['edges'][number]>(null);
  const [mutate] = useBulkUpdateGrievanceAssigneeMutation();
  const [inputValue, setInputValue] = useState('');
  const { data: usersData } = useAllUsersForFiltersQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'first_name,last_name,email',
      search: inputValue,
    },
  });
  const optionsData = usersData?.allUsers?.edges || [];
  const onFilterChange = (data): void => {
    if (data) {
      setValue(data);
    }
  };
  const onSave = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          assignedTo: value.node.id,
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
