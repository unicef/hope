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
import { Dialog } from '../../../containers/dialogs/Dialog';
import {
  decodeIdString,
  grievanceTicketStatusToColor,
} from '../../../utils/utils';
import {
  AllGrievanceTicketQuery,
  useExistingGrievanceTicketsLazyQuery,
} from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import {
  DialogFooter,
  DialogTitleWrapper,
} from '../../core/ConfirmationDialog/ConfirmationDialog';
import { LoadingComponent } from '../../core/LoadingComponent';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';

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
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
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
  const [
    loadExistingTickets,
    { data, loading },
  ] = useExistingGrievanceTicketsLazyQuery({
    variables: {
      businessArea,
      household:
        decodeIdString(ticket.household?.id) ||
        '294cfa7e-b16f-4331-8014-a22ffb2b8b3c',
      //adding some random ID to get 0 results if there is no household id.
    },
  });
  useEffect(() => {
    loadExistingTickets();
  }, [dialogOpen, loadExistingTickets]);

  const history = useHistory();
  const { t } = useTranslation();
  const linkedTickets = ticket.relatedTickets;

  if (loading) return <LoadingComponent />;
  if (!data) return null;

  const existingTickets = data.existingGrievanceTickets;

  const renderRow = (row): React.ReactElement => {
    const issueType = row.issueType
      ? issueTypeChoicesData
          .filter((el) => el.category === row.category.toString())[0]
          .subCategories.filter(
            (el) => el.value === row.issueType.toString(),
          )[0].name
      : '-';

    return (
      <ClickableTableRow
        hover
        onClick={
          canViewDetails
            ? () =>
                history.push(
                  `/${businessArea}/grievance-and-feedback/${row.id}`,
                )
            : undefined
        }
        key={row.id}
      >
        <TableCell align='left'>
          {canViewDetails ? (
            <BlackLink to={`/${businessArea}/grievance-and-feedback/${row.id}`}>
              {row.unicefId}
            </BlackLink>
          ) : (
            row.unicefId
          )}
        </TableCell>
        <TableCell align='left'>{categoryChoices[row.category]}</TableCell>
        <TableCell align='left'>{issueType || '-'}</TableCell>
        <TableCell align='left'>
          <StatusContainer>
            <StatusBox
              status={statusChoices[row.status]}
              statusToColor={grievanceTicketStatusToColor}
            />
          </StatusContainer>
        </TableCell>
      </ClickableTableRow>
    );
  };

  const renderLink = (): React.ReactElement => {
    const ticketsCount = linkedTickets.length + existingTickets.totalCount;
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
          <DialogTitle id='scroll-dialog-title'>
            {t('Linked Tickets')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <Typography>
              <Bold>Ticket ID {ticket.unicefId} </Bold>
              is linked to following related tickets.
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
            <TableBody>
              {linkedTickets.map((linkedTicket) => renderRow(linkedTicket))}
              {existingTickets.edges.map((existingTicket) =>
                renderRow(existingTicket.node),
              )}
            </TableBody>
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
