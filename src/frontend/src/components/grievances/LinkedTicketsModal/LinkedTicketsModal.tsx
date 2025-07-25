import { Bold } from '@components/core/Bold';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { grievanceTicketStatusToColor } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { getGrievanceDetailsPath } from '../utils/createGrievanceUtils';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 100px;
`;
const StyledDialog = styled(Dialog)`
  max-height: 800px;
`;

interface LinkedTicketsModalProps {
  ticket: GrievanceTicketList;
  categoryChoices: { [id: number]: string };
  statusChoices: { [id: number]: string };
  canViewDetails: boolean;
  baseUrl: string;
  issueTypeChoicesData;
}

function LinkedTicketsModal({
  ticket,
  categoryChoices,
  statusChoices,
  canViewDetails,
  baseUrl,
  issueTypeChoicesData,
}: LinkedTicketsModalProps): ReactElement {
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const renderIssueTypeName = (row): string => {
    if (!row.issueType) {
      return '-';
    }

    return issueTypeChoicesData
      .find((el) => el.category === row.category.toString())
      ?.subCategories.find((el) => el.value === row.issueType.toString()).name;
  };

  const renderRow = (row): ReactElement => {
    const issueType = renderIssueTypeName(row);
    const grievanceDetailsPath = getGrievanceDetailsPath(
      row.id,
      row.category,
      baseUrl,
    );
    return (
      <ClickableTableRow
        hover
        onClick={
          canViewDetails ? () => navigate(grievanceDetailsPath) : undefined
        }
        key={row.id}
      >
        <TableCell align="left">
          {canViewDetails ? (
            <BlackLink to={grievanceDetailsPath}>{row.unicefId}</BlackLink>
          ) : (
            row.unicefId
          )}
        </TableCell>
        <TableCell align="left">{categoryChoices[row.category]}</TableCell>
        <TableCell align="left">{issueType || '-'}</TableCell>
        <TableCell align="left">
          <StatusBox
            status={statusChoices[row.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </TableCell>
      </ClickableTableRow>
    );
  };

  const renderLink = (): ReactElement => {
    const ticketsCount = ticket.relatedTickets.length;
    if (ticketsCount === 0) {
      return <span>-</span>;
    }
    return (
      <StyledLink
        onClick={(e) => {
          e.stopPropagation();
          setDialogOpen(true);
        }}
      >
        {ticketsCount} linked ticket
        {ticketsCount === 1 ? '' : 's'}
      </StyledLink>
    );
  };

  const renderRows = (): ReactElement => {
    const { relatedTickets } = ticket || {};
    return (
      <>{relatedTickets.map((relatedTicket) => renderRow(relatedTicket))}</>
    );
  };

  return (
    <>
      {renderLink()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="lg"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Related Tickets')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <Typography>
              <Bold>
                Ticket ID
                {ticket.unicefId}
              </Bold>
              is related to the following tickets.
            </Typography>
          </Box>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell align="left">{t('Ticket Id')}</TableCell>
                <TableCell align="left">{t('Category')}</TableCell>
                <TableCell align="left">{t('Issue Type')}</TableCell>
                <TableCell align="left">{t('Status')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>{renderRows()}</TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                setDialogOpen(false);
              }}
            >
              {t('CANCEL')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </StyledDialog>
    </>
  );
}

export default withErrorBoundary(LinkedTicketsModal, 'LinkedTicketsModal');
