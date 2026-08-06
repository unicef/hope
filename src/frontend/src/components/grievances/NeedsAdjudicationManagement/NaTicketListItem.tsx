import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import WarningIcon from '@mui/icons-material/Warning';
import { Box, Typography } from '@mui/material';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { grievanceTicketBadgeColors } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { getIssueTypeToDisplay } from '../utils/createGrievanceUtils';

interface NaTicketListItemProps {
  ticket: GrievanceTicketList;
  urgencyChoices: Array<Record<string, any>>;
  selected: boolean;
  managed: boolean;
  needsReassignment: boolean;
  onSelect: () => void;
}

export const NaTicketListItem = ({
  ticket,
  urgencyChoices,
  selected,
  managed,
  needsReassignment,
  onSelect,
}: NaTicketListItemProps): ReactElement => {
  const { t } = useTranslation();
  const urgencyLabel =
    urgencyChoices.find((choice) => choice.value === ticket.urgency)?.name ||
    '-';
  const issueTypeToDisplay = getIssueTypeToDisplay(ticket.issueType);

  return (
    <Box
      onClick={onSelect}
      data-cy={`na-ticket-list-item-${ticket.unicefId}`}
      sx={{
        p: 4,
        borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'stretch',
        cursor: 'pointer',
        backgroundColor: selected ? 'rgba(0, 0, 0, 0.06)' : 'transparent',
        '&:hover': {
          backgroundColor: selected
            ? 'rgba(0, 0, 0, 0.06)'
            : 'rgba(0, 0, 0, 0.03)',
        },
      }}
    >
      <Box>
        <Typography variant="subtitle1">
          {t('Ticket ID')}: {ticket.unicefId}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {issueTypeToDisplay}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          <UniversalMoment>{ticket.createdAt}</UniversalMoment>
        </Typography>
      </Box>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          alignItems: 'flex-end',
        }}
      >
        <StatusBox
          status={urgencyLabel}
          statusToColor={grievanceTicketBadgeColors}
        />
        {needsReassignment ? (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              color: 'warning.main',
            }}
          >
            <WarningIcon fontSize="small" />
            <Typography
              variant="body2"
              sx={{ fontStyle: 'italic' }}
              data-cy="na-ticket-reassignment-required"
            >
              {t('Reassignment required')}
            </Typography>
          </Box>
        ) : (
          managed && (
            <Typography
              variant="body2"
              color="textSecondary"
              sx={{ fontStyle: 'italic' }}
              data-cy="na-ticket-managed-label"
            >
              {t('Ticket managed')}
            </Typography>
          )
        )}
      </Box>
    </Box>
  );
};
