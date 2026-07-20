import { BlackLink } from '@core/BlackLink';
import { LoadingComponent } from '@core/LoadingComponent';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Box,
  Button,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ApproveBox,
  StyledTable,
} from '../GrievancesApproveSection/ApproveSectionStyles';
import { getGrievanceDetailsPath } from '../utils/createGrievanceUtils';

// Light red used to flag fields whose values differ between the two individuals.
const DIFF_BACKGROUND = '#fdecea';

interface NaComparisonPanelProps {
  ticketId: string | null;
}

interface ComparisonRow {
  label: string;
  // Rendered cell content for a given individual.
  render: (individual: any) => ReactNode;
  // Comparable string used to decide whether the two values differ.
  compare: (individual: any) => string;
}

const comparisonRows: ComparisonRow[] = [
  {
    label: 'Full Name',
    render: (i) => i?.fullName || '-',
    compare: (i) => i?.fullName ?? '',
  },
  {
    label: 'Date of Birth',
    render: (i) => <UniversalMoment>{i?.birthDate}</UniversalMoment>,
    compare: (i) => i?.birthDate ?? '',
  },
  {
    label: 'Sex',
    render: (i) => i?.sex || '-',
    compare: (i) => i?.sex ?? '',
  },
  {
    label: 'Document',
    render: (i) =>
      i?.documents?.[0]
        ? `${i.documents[0].type?.label ?? ''} ${i.documents[0].documentNumber ?? ''}`.trim()
        : '-',
    compare: (i) =>
      i?.documents?.[0]
        ? `${i.documents[0].type?.label ?? ''} ${i.documents[0].documentNumber ?? ''}`
        : '',
  },
  {
    label: 'Village',
    render: (i) => i?.household?.village || i?.household?.admin2?.name || '-',
    compare: (i) => i?.household?.village || i?.household?.admin2?.name || '',
  },
];

const findSimilarity = (records, individualId): number | undefined =>
  records?.find((record) => record.hitId === individualId)?.score;

export const NaComparisonPanel = ({
  ticketId,
}: NaComparisonPanelProps): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl, businessAreaSlug } = useBaseUrl();

  const { data: ticket, isLoading } = useQuery<GrievanceTicketDetail>({
    queryKey: ['businessAreasGrievanceTicketsRetrieve', businessAreaSlug, ticketId],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug,
        id: ticketId,
      }),
    enabled: !!ticketId,
  });

  if (!ticketId) {
    return (
      <ApproveBox>
        <Typography variant="body2" color="textSecondary">
          {t('Select a ticket to compare individuals')}
        </Typography>
      </ApproveBox>
    );
  }

  if (isLoading || !ticket) {
    return (
      <ApproveBox>
        <LoadingComponent />
      </ApproveBox>
    );
  }

  const detailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );

  const details = ticket.ticketDetails;
  const person1 = details?.goldenRecordsIndividual;
  const person2 =
    details?.possibleDuplicate ?? details?.possibleDuplicates?.[0];

  const similarity =
    findSimilarity(details?.extraData?.possibleDuplicate, person1?.id) ??
    findSimilarity(person2?.deduplicationGoldenRecordResults, person1?.id) ??
    findSimilarity(details?.extraData?.goldenRecords, person2?.id);

  return (
    <ApproveBox>
      <Box mb={4}>
        <Typography variant="h6">
          Ticket ID:{' '}
          {detailsPath ? (
            <BlackLink to={detailsPath}>
              <u>{ticket.unicefId}</u>
            </BlackLink>
          ) : (
            <u>{ticket.unicefId}</u>
          )}
        </Typography>
      </Box>
      <StyledTable data-cy="na-comparison-table">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell align="left">{t('Person 1')}</TableCell>
            <TableCell align="left">{t('Person 2')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {comparisonRows.map((row) => {
            const differs = row.compare(person1) !== row.compare(person2);
            return (
              <TableRow
                key={row.label}
                data-cy={`na-comparison-row-${row.label}`}
                sx={
                  differs ? { backgroundColor: DIFF_BACKGROUND } : undefined
                }
              >
                <TableCell align="left">{t(row.label)}</TableCell>
                <TableCell align="left">{row.render(person1)}</TableCell>
                <TableCell align="left">{row.render(person2)}</TableCell>
              </TableRow>
            );
          })}
          <TableRow>
            <TableCell align="left">{t('Similarity score')}</TableCell>
            <TableCell align="center" colSpan={2}>
              {typeof similarity === 'number' ? `${similarity}%` : '-'}
            </TableCell>
          </TableRow>
          {/* TODO: wire Withdraw / Not Duplicates / Clear to approve-needs-adjudication */}
          <TableRow>
            <TableCell align="left">{t('Withdraw')}</TableCell>
            <TableCell align="center">
              <Button
                variant="outlined"
                color="primary"
                fullWidth
                data-cy="button-na-withdraw-person1"
                onClick={() => {
                  // TODO: withdraw Person 1
                }}
              >
                {t('Withdraw')}
              </Button>
            </TableCell>
            <TableCell align="center">
              <Button
                variant="outlined"
                color="primary"
                fullWidth
                data-cy="button-na-withdraw-person2"
                onClick={() => {
                  // TODO: withdraw Person 2
                }}
              >
                {t('Withdraw')}
              </Button>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align="center" colSpan={2}>
              <Button
                variant="outlined"
                color="primary"
                fullWidth
                data-cy="button-na-not-duplicates"
                onClick={() => {
                  // TODO: mark the two individuals as not duplicates
                }}
              >
                {t('Not Duplicates')}
              </Button>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align="center" colSpan={2}>
              <Button
                color="primary"
                data-cy="button-na-clear"
                onClick={() => {
                  // TODO: clear the current selection
                }}
              >
                {t('Clear')}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </ApproveBox>
  );
};
