import {
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '../../../containers/dialogs/Dialog';
import {
  grievanceTicketStatusToColor,
  renderUserName,
} from '../../../utils/utils';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import {
  DialogFooter,
  DialogTitleWrapper,
} from '../../core/ConfirmationDialog/ConfirmationDialog';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';

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
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LinkedTicketsModalProps {
  linkedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']['relatedTickets'];
  categoryChoices: { [id: number]: string };
  statusChoices: { [id: number]: string };
  canViewDetails: boolean;
  businessArea: string;
}

export const LinkedTicketsModal = ({
  linkedTickets,
  categoryChoices,
  statusChoices,
  canViewDetails,
  businessArea,
}: LinkedTicketsModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const history = useHistory();
  const { t } = useTranslation();

  return (
    <>
      {linkedTickets.length ? (
        <StyledLink
          onClick={(e) => {
            e.stopPropagation();
            setDialogOpen(true);
          }}
        >
          {linkedTickets.length} linked ticket
          {linkedTickets.length === 1 ? '' : 's'}
        </StyledLink>
      ) : (
        '-'
      )}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Linked Tickets')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell align='left'>{t('ID')}</TableCell>
                <TableCell align='left'>{t('Status')}</TableCell>
                <TableCell align='left'>{t('Category')}</TableCell>
                <TableCell align='left'>{t('Issue Type')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {linkedTickets.map((ticket) => (
                <ClickableTableRow
                  hover
                  onClick={
                    canViewDetails
                      ? history.push(
                          `/${businessArea}/grievance-and-feedback/${ticket.id}`,
                        )
                      : undefined
                  }
                  key={ticket.id}
                >
                  <TableCell align='left'>
                    {canViewDetails ? (
                      <BlackLink
                        to={`/${businessArea}/grievance-and-feedback/${ticket.id}`}
                      >
                        {ticket.unicefId}
                      </BlackLink>
                    ) : (
                      ticket.unicefId
                    )}
                  </TableCell>
                  <TableCell align='left'>
                    <StatusContainer>
                      <StatusBox
                        status={statusChoices[ticket.status]}
                        statusToColor={grievanceTicketStatusToColor}
                      />
                    </StatusContainer>
                  </TableCell>

                  <TableCell align='left'>
                    {categoryChoices[ticket.category]}
                  </TableCell>
                  <TableCell align='left'>{ticket.issueType || '-'}</TableCell>
                </ClickableTableRow>
              ))}
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
      </Dialog>
    </>
  );
};
