import { useConfirmation } from '@core/ConfirmationDialog';
import { LoadingComponent } from '@core/LoadingComponent';
import { Box, Paper, TablePagination, Typography } from '@mui/material';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { NaTicketListItem } from './NaTicketListItem';

interface NaTicketsListProps {
  tickets: GrievanceTicketList[];
  isLoading: boolean;
  choicesData?: GrievanceChoices;
  selectedTicketId: string | null;
  onSelect: (id: string) => void;
  page: number;
  rowsPerPage: number;
  count: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (rowsPerPage: number) => void;
}

export const NaTicketsList = ({
  tickets,
  isLoading,
  choicesData,
  selectedTicketId,
  onSelect,
  page,
  rowsPerPage,
  count,
  onPageChange,
  onRowsPerPageChange,
}: NaTicketsListProps): ReactElement => {
  const { t } = useTranslation();
  const confirm = useConfirmation();

  const urgencyChoices = choicesData?.grievanceTicketUrgencyChoices ?? [];

  // Requirement: changing the page opens a confirmation modal first.
  // TODO: replace the placeholder copy once the resolution flow is defined.
  const confirmPageChange = (apply: () => void): void => {
    confirm({
      title: t('Change page'),
      content: t(
        'TODO: placeholder — you are about to leave the current page. Continue?',
      ),
    }).then(apply, () => undefined);
  };

  return (
    <Paper>
      <Box maxHeight="60vh" overflow="auto">
        {isLoading ? (
          <LoadingComponent />
        ) : tickets.length === 0 ? (
          <Box p={5}>
            <Typography variant="body2" color="textSecondary">
              {t('No Needs Adjudication tickets')}
            </Typography>
          </Box>
        ) : (
          tickets.map((ticket) => (
            <NaTicketListItem
              key={ticket.id}
              ticket={ticket}
              urgencyChoices={urgencyChoices}
              selected={ticket.id === selectedTicketId}
              onSelect={() => onSelect(ticket.id)}
            />
          ))
        )}
      </Box>
      <TablePagination
        component="div"
        count={count}
        page={page}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={[10, 15, 20]}
        showFirstButton
        showLastButton
        onPageChange={(_event, newPage) =>
          confirmPageChange(() => onPageChange(newPage))
        }
        onRowsPerPageChange={(event) => {
          const value = parseInt(event.target.value, 10);
          confirmPageChange(() => onRowsPerPageChange(value));
        }}
        data-cy="na-tickets-pagination"
      />
    </Paper>
  );
};
