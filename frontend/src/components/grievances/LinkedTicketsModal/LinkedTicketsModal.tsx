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
} from '@material-ui/core';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  AllGrievanceTicketQuery,
  useRelatedGrievanceTicketsLazyQuery,
} from '../../../__generated__/graphql';
import { Dialog } from '../../../containers/dialogs/Dialog';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { grievanceTicketStatusToColor } from '../../../utils/utils';
import { BlackLink } from '../../core/BlackLink';
import { LoadingComponent } from '../../core/LoadingComponent';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
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

const Bold = styled.span`
  font-weight: bold;
`;

interface LinkedTicketsModalProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  categoryChoices: { [id: number]: string };
  statusChoices: { [id: number]: string };
  canViewDetails: boolean;
  businessArea: string;
  issueTypeChoicesData;
}

export const LinkedTicketsModal = ({
  ticket,
  categoryChoices,
  statusChoices,
  canViewDetails,
  businessArea,
  issueTypeChoicesData,
}: LinkedTicketsModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const history = useHistory();
  const { t } = useTranslation();
  const [
    loadRelatedTickets,
    { data, loading },
  ] = useRelatedGrievanceTicketsLazyQuery({
    variables: {
      id: ticket.id,
    },
  });
  useEffect(() => {
    if (dialogOpen) {
      loadRelatedTickets();
    }
  }, [dialogOpen, loadRelatedTickets]);

  const renderIssueTypeName = (row): string => {
    if (!row.issueType) {
      return '-';
    }

    return issueTypeChoicesData
      .find((el) => el.category === row.category.toString())
      .subCategories.find((el) => el.value === row.issueType.toString()).name;
  };

  const renderRow = (row): React.ReactElement => {
    const issueType = renderIssueTypeName(row);

    return (
      <ClickableTableRow
        hover
        onClick={
          canViewDetails
            ? () =>
                history.push(
                  getGrievanceDetailsPath(row.id, row.category, businessArea),
                )
            : undefined
        }
        key={row.id}
      >
        <TableCell align='left'>
          {canViewDetails ? (
            <BlackLink
              to={getGrievanceDetailsPath(row.id, row.category, businessArea)}
            >
              {row.unicefId}
            </BlackLink>
          ) : (
            row.unicefId
          )}
        </TableCell>
        <TableCell align='left'>{categoryChoices[row.category]}</TableCell>
        <TableCell align='left'>{issueType || '-'}</TableCell>
        <TableCell align='left'>
          <StatusBox
            status={statusChoices[row.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </TableCell>
      </ClickableTableRow>
    );
  };

  const renderLink = (): React.ReactElement => {
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

  const renderRows = (): React.ReactElement => {
    if (loading) return <LoadingComponent />;
    if (!data) return null;

    const { relatedTickets } = data?.grievanceTicket;
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
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='lg'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Related Tickets')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <Typography>
              <Bold>Ticket ID {ticket.unicefId} </Bold>
              is related to the following tickets.
            </Typography>
          </Box>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell align='left'>{t('Ticket Id')}</TableCell>
                <TableCell align='left'>{t('Category')}</TableCell>
                <TableCell align='left'>{t('Issue Type')}</TableCell>
                <TableCell align='left'>{t('Status')}</TableCell>
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
};
