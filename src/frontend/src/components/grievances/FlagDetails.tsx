import {
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import styled from 'styled-components';
import moment from 'moment';
import { useTranslation } from 'react-i18next';
import { DATE_FORMAT } from '../../config';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useConfirmation } from '@core/ConfirmationDialog';
import { FlagTooltip } from '@core/FlagTooltip';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { ViewSanctionList } from './ViewSanctionList';
import { ReactElement } from 'react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export const FlagDetails = ({
  ticket,
  canApproveFlag,
}: {
  ticket: GrievanceTicketDetail;
  canApproveFlag: boolean;
}): ReactElement => {
  const { t } = useTranslation();
  const confirm = useConfirmation();
  const { businessArea } = useBaseUrl();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({
      grievanceTicketId,
      approveStatus,
    }: {
      grievanceTicketId: string;
      approveStatus: boolean;
    }) =>
      RestService.restBusinessAreasGrievanceTicketsApproveStatusUpdateCreate({
        businessAreaSlug: businessArea,
        id: grievanceTicketId,
        requestBody: {
          approveStatus,
        },
      }),
    onSuccess: () => {
      // Invalidate and refetch the grievance ticket details
      queryClient.invalidateQueries({
        queryKey: ['grievanceTicket', ticket.id],
      });
    },
  });

  const confirmationText = t(
    'Are you sure you want to confirm flag (sanction list match) ?',
  );
  const removalText = t('Are you sure you want to remove the flag ?');
  const details = ticket.ticketDetails;
  const isFlagConfirmed = details.approveStatus;
  return (
    <ApproveBox>
      <Title>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">{t('Flag Details')}</Typography>
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
                    mutation.mutateAsync({
                      grievanceTicketId: ticket.id,
                      approveStatus: !details.approveStatus,
                    }),
                  )
                }
                variant="outlined"
                color="primary"
              >
                {isFlagConfirmed ? t('REMOVE FLAG') : t('CONFIRM FLAG')}
              </Button>
            )}
          </Box>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align="left" />
            <TableCell align="left">{t('Ref. No. on Sanction List')}</TableCell>
            <TableCell align="left">{t('Full Name')}</TableCell>
            <TableCell align="left">{t('Date of Birth')}</TableCell>
            <TableCell align="left">{t('National Ids')}</TableCell>
            <TableCell align="left">{t('Source')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align="left">
              {isFlagConfirmed ? (
                <FlagTooltip
                  message={t('Sanction List Confirmed Match')}
                  confirmed
                />
              ) : (
                ''
              )}
            </TableCell>
            <TableCell align="left">-</TableCell>
            <TableCell align="left">
              {details.goldenRecordsIndividual.fullName}
            </TableCell>
            <TableCell align="left">
              <UniversalMoment>
                {details.goldenRecordsIndividual.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align="left">
              {details.goldenRecordsIndividual.documents
                .filter((item) => item.type.key === 'NATIONAL_ID')
                .map((item) => item.documentNumber)
                .join(', ') || '-'}
            </TableCell>
            <TableCell align="left">{t('Golden Record')}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left" />
            <TableCell align="left">
              {details.sanctionListIndividual.referenceNumber}
            </TableCell>
            <TableCell align="left">
              {details.sanctionListIndividual.fullName}
            </TableCell>
            <TableCell align="left">
              {details.sanctionListIndividual.datesOfBirth
                .map((item) => moment(item.date).format(DATE_FORMAT))
                .join(', ') || '-'}
            </TableCell>
            <TableCell align="left">
              {details.sanctionListIndividual.documents
                .map((item) => item.documentNumber)
                .join(', ') || '-'}
            </TableCell>
            <TableCell align="left">{t('Sanction List')}</TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </ApproveBox>
  );
};
