import {
  Box,
  Button,
  makeStyles,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { DATE_FORMAT } from '../../config';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import {
  GrievanceTicketDocument,
  GrievanceTicketNode,
  useApproveSystemFlaggingMutation,
} from '../../__generated__/graphql';
import { useConfirmation } from '../core/ConfirmationDialog';
import { FlagTooltip } from '../core/FlagTooltip';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { ViewSanctionList } from './ViewSanctionList';

export function FlagDetails({
  ticket,
  canApproveFlag,
}: {
  ticket: GrievanceTicketNode;
  canApproveFlag: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const confirm = useConfirmation();
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const [approve] = useApproveSystemFlaggingMutation({
    refetchQueries: () => [
      {
        query: GrievanceTicketDocument,
        variables: { id: ticket.id },
      },
    ],
  });
  const classes = useStyles();
  const confirmationText = t(
    'Are you sure you want to confirm flag (sanction list match) ?',
  );
  const removalText = t('Are you sure you want to remove the flag ?');
  const details = ticket.systemFlaggingTicketDetails;
  const isFlagConfirmed = details.approveStatus;
  return (
    <ApproveBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Flag Details')}</Typography>
          <Box>
            <ViewSanctionList
              referenceNumber={details.sanctionListIndividual.referenceNumber}
            />
            {canApproveFlag && (
              <Button
                disabled={
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                onClick={() =>
                  confirm({
                    content: isFlagConfirmed ? removalText : confirmationText,
                  }).then(() =>
                    approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        approveStatus: !details.approveStatus,
                      },
                    }),
                  )
                }
                variant='outlined'
                color='primary'
              >
                {isFlagConfirmed ? t('REMOVE FLAG') : t('CONFIRM FLAG')}
              </Button>
            )}
          </Box>
        </Box>
      </Title>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>{t('Ref. No. on Sanction List')}</TableCell>
            <TableCell align='left'>{t('Full Name')}</TableCell>
            <TableCell align='left'>{t('Date of Birth')}</TableCell>
            <TableCell align='left'>{t('National Ids')}</TableCell>
            <TableCell align='left'>{t('Source')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>
              {isFlagConfirmed ? (
                <FlagTooltip
                  message={t('Sanction List Confirmed Match')}
                  confirmed
                />
              ) : (
                ''
              )}
            </TableCell>
            <TableCell align='left'>-</TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual.fullName}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.goldenRecordsIndividual.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual.documents.edges
                .filter((item) => item.node.type.type === 'NATIONAL_ID')
                .map((item) => item.node.documentNumber)
                .join(', ') || '-'}
            </TableCell>
            <TableCell align='left'>{t('Golden Record')}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>
              {details.sanctionListIndividual.referenceNumber}
            </TableCell>
            <TableCell align='left'>
              {details.sanctionListIndividual.fullName}
            </TableCell>
            <TableCell align='left'>
              {details.sanctionListIndividual.datesOfBirth.edges
                .map((item) => moment(item.node.date).format(DATE_FORMAT))
                .join(', ') || '-'}
            </TableCell>
            <TableCell align='left'>
              {details.sanctionListIndividual.documents.edges
                .map((item) => item.node.documentNumber)
                .join(', ') || '-'}
            </TableCell>
            <TableCell align='left'>{t('Sanction List')}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </ApproveBox>
  );
}
