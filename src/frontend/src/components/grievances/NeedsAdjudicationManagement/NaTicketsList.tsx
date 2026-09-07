import { useConfirmation } from '@core/ConfirmationDialog';
import { LoadingComponent } from '@core/LoadingComponent';
import { Box, Paper, TablePagination, Typography } from '@mui/material';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { NaTicketListItem } from './NaTicketListItem';
import { isDecisionComplete, isDecisionResolved } from './naRoleUtils';
import { NaTicketDecision } from './naTypes';

interface NaTicketsListProps {
  tickets: GrievanceTicketList[];
  isLoading: boolean;
  choicesData?: GrievanceChoices;
  selectedTicketId: string | null;
  decisions: Record<string, NaTicketDecision>;
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
  decisions,
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

  const managedCount = Object.keys(decisions).length;

  // Changing the page only needs a confirmation when the operator is carrying
  // decisions that have not been finalized yet.
  const confirmPageChange = (apply: () => void): void => {
    if (managedCount === 0) {
      apply();
      return;
    }
    confirm({
      catchOnCancel: true,
      title: t('Change page'),
      content: t(
        'You have {{count}} ticket(s) managed but not finalized. Your decisions are kept when you change page, but nothing is saved until you click Finalize. Continue?',
        { count: managedCount },
      ),
    }).then(apply, () => undefined);
  };

  return (
    <Paper
      sx={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        minHeight: 0,
      }}
    >
      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          maxHeight: { xs: '60vh', md: 'none' },
          overflow: 'auto',
        }}
      >
        {isLoading ? (
          <LoadingComponent />
        ) : tickets.length === 0 ? (
          <Box sx={{ p: 5 }}>
            <Typography variant="body2" color="textSecondary">
              {t('No Needs Adjudication tickets')}
            </Typography>
          </Box>
        ) : (
          tickets.map((ticket) => {
            const decision = decisions[ticket.id];
            return (
              <NaTicketListItem
                key={ticket.id}
                ticket={ticket}
                urgencyChoices={urgencyChoices}
                selected={ticket.id === selectedTicketId}
                managed={!!decision}
                needsReassignment={!!decision && !isDecisionResolved(decision)}
                incomplete={!!decision && !isDecisionComplete(decision)}
                onSelect={() => onSelect(ticket.id)}
              />
            );
          })
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
