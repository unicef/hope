import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { Typography } from '@mui/material';
import { BulkCloseGrievanceTickets } from '@restgenerated/models/BulkCloseGrievanceTickets';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { BulkBaseModal } from './BulkBaseModal';

interface BulkCloseModalProps {
  selectedTickets: GrievanceTicketList[];
  setSelected: (tickets: GrievanceTicketList[]) => void;
}

export function BulkCloseModal({
  selectedTickets,
  setSelected,
}: BulkCloseModalProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessAreaSlug, isAllPrograms } = useBaseUrl();
  const queryClient = useQueryClient();

  // Only Grievance Complaint tickets in For Approval can be closed. The whole
  // batch must be closable, otherwise nothing is closed.
  const notClosableCount = selectedTickets.filter(
    (ticket) =>
      ticket.category.toString() !== GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT ||
      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL,
  ).length;
  const allClosable = selectedTickets.length > 0 && notClosableCount === 0;

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkCloseGrievanceTickets) =>
      RestService.restBusinessAreasGrievanceTicketsBulkCloseCreate({
        businessAreaSlug,
        formData: params,
      }),
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
      showMessage(
        t('{{count}} ticket(s) closed.', { count: selectedTickets.length }),
      );
      setSelected([]);
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const onSave = async (): Promise<void> => {
    await mutateAsync({
      grievanceTicketIds: selectedTickets.map((ticket) => ticket.id),
    });
  };

  return (
    <BulkBaseModal
      selectedTickets={selectedTickets}
      title={t('Close Tickets')}
      buttonTitle={t('close tickets')}
      saveLabel={t('CLOSE TICKETS')}
      onSave={onSave}
      icon={<CheckCircleIcon />}
      disabledSave={!allClosable}
    >
      {allClosable ? (
        <Typography data-cy="close-summary">
          {t('{{count}} ticket(s) will be closed.', {
            count: selectedTickets.length,
          })}
        </Typography>
      ) : (
        <Typography color="error" data-cy="close-blocked-summary">
          {t(
            '{{count}} of the selected ticket(s) cannot be closed. Only Grievance Complaint tickets in status For Approval can be closed — deselect the others to continue.',
            { count: notClosableCount },
          )}
        </Typography>
      )}
    </BulkBaseModal>
  );
}
