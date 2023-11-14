import { MenuItem, Select } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import PriorityHighIcon from '@material-ui/icons/PriorityHigh';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  AllGrievanceTicketQuery,
  useBulkUpdateGrievanceUrgencyMutation,
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

interface BulkSetUrgencyModalProps {
  selectedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][];
  businessArea: string;
  setSelected;
}

export const BulkSetUrgencyModal = ({
  selectedTickets,
  businessArea,
  setSelected,
}: BulkSetUrgencyModalProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [value, setValue] = React.useState<number>(0);
  const [mutate] = useBulkUpdateGrievanceUrgencyMutation();
  const { data: choices } = useGrievancesChoiceDataQuery();
  const urgencyChoices = choices.grievanceTicketUrgencyChoices;
  const onSave = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          urgency: value,
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
    <>
      <BulkBaseModal
        selectedTickets={selectedTickets}
        title={t('Set Urgency')}
        buttonTitle={t('Set Urgency')}
        onSave={onSave}
        icon={<PriorityHighIcon />}
      >
        <Select
          value={value}
          onChange={(e) => setValue(e.target.value as number)}
          style={{ width: '100%' }}
          variant='outlined'
          margin='dense'
          label={t('Urgency')}
        >
          {urgencyChoices.map((choice) => (
            <MenuItem value={choice.value}>{choice.name}</MenuItem>
          ))}
        </Select>
      </BulkBaseModal>
    </>
  );
};
