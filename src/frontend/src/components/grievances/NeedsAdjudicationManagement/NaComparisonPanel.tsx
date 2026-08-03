import { BlackLink } from '@core/BlackLink';
import { LoadingComponent } from '@core/LoadingComponent';
import { UniversalMoment } from '@core/UniversalMoment';
import { GrievanceIndividualPhotoModal } from '@components/grievances/GrievancesPhotoModals/GrievanceIndividualPhotoModal';
import { useBaseUrl } from '@hooks/useBaseUrl';
import PeopleIcon from '@mui/icons-material/People';
import PersonIcon from '@mui/icons-material/Person';
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
import { ReactElement, ReactNode, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ApproveBox,
  StyledTable,
} from '../GrievancesApproveSection/ApproveSectionStyles';
import { getGrievanceDetailsPath } from '../utils/createGrievanceUtils';
import { NaReassignRoleModal } from './NaReassignRoleModal';
import {
  getRequiredReassignments,
  keyReassignments,
  NaIndividual,
  reassignmentKey,
  roleLabel,
} from './naRoleUtils';
import { NaMark, NaRoleAssignment, NaTicketDecision } from './naTypes';

// Light red used to flag fields whose values differ between the two individuals.
const DIFF_BACKGROUND = '#fdecea';

interface NaComparisonPanelProps {
  ticketId: string | null;
  decision?: NaTicketDecision;
  onDecide: (decision: NaTicketDecision) => void;
  onReassign: (
    key: string,
    newIndividual: { id: string; fullName?: string },
  ) => void;
  onClear: () => void;
}

// Duplicate → two-people icon; unique → one-person icon; no mark → nothing.
const PersonMarkIcon = ({
  role,
}: {
  role: 'duplicate' | 'unique' | undefined;
}): ReactElement | null => {
  if (role === 'duplicate') return <PeopleIcon fontSize="small" />;
  if (role === 'unique') return <PersonIcon fontSize="small" />;
  return null;
};

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
  {
    label: 'Photo',
    render: (i) =>
      i?.id ? (
        <GrievanceIndividualPhotoModal individualId={i.id} isCurrent />
      ) : (
        '-'
      ),
    // Photos are expected to differ between two distinct individuals, so
    // don't apply the "differs" highlight to this row.
    compare: () => '',
  },
];

const findSimilarity = (records, individualId): number | undefined =>
  records?.find((record) => record.hitId === individualId)?.score;

export const NaComparisonPanel = ({
  ticketId,
  decision,
  onDecide,
  onReassign,
  onClear,
}: NaComparisonPanelProps): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl, businessAreaSlug } = useBaseUrl();
  // Which reassignment row currently has its picker open.
  const [openReassignKey, setOpenReassignKey] = useState<string | null>(null);
  const mark = decision?.mark;

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
  const person2 = details?.possibleDuplicate ?? details?.possibleDuplicates?.[0];

  // Withdrawing a person marks them duplicate and the other one distinct; any
  // HEAD/PRIMARY role they hold in a surviving household must be handed over
  // before this ticket can be executed.
  const withdraw = (mark: NaMark, duplicate: NaIndividual): void => {
    const other = duplicate === person1 ? person2 : person1;
    onDecide({
      mark,
      duplicateIndividualIds: [duplicate?.id].filter(Boolean),
      distinctIndividualIds: [other?.id].filter(Boolean),
      reassignments: keyReassignments(getRequiredReassignments(duplicate)),
    });
  };

  const markNotDuplicates = (): void =>
    onDecide({
      mark: 'not_duplicates',
      duplicateIndividualIds: [],
      distinctIndividualIds: [person1?.id, person2?.id].filter(Boolean),
      reassignments: {},
    });

  const reassignments: NaRoleAssignment[] = Object.values(
    decision?.reassignments ?? {},
  );
  const openReassignment = openReassignKey
    ? decision?.reassignments[openReassignKey]
    : undefined;
  const duplicateIndividual =
    mark === 'person1_duplicate'
      ? person1
      : mark === 'person2_duplicate'
        ? person2
        : undefined;

  const similarity =
    findSimilarity(details?.extraData?.possibleDuplicate, person1?.id) ??
    findSimilarity(person2?.deduplicationGoldenRecordResults, person1?.id) ??
    findSimilarity(details?.extraData?.goldenRecords, person2?.id);

  // Which header icon each person shows, derived from the current mark.
  const person1Role =
    mark === 'person1_duplicate'
      ? 'duplicate'
      : mark === 'person2_duplicate' || mark === 'not_duplicates'
        ? 'unique'
        : undefined;
  const person2Role =
    mark === 'person2_duplicate'
      ? 'duplicate'
      : mark === 'person1_duplicate' || mark === 'not_duplicates'
        ? 'unique'
        : undefined;

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
            <TableCell align="left">
              <Box display="flex" alignItems="center" gap={1}>
                {t('Person 1')}
                <PersonMarkIcon role={person1Role} />
              </Box>
            </TableCell>
            <TableCell align="left">
              <Box display="flex" alignItems="center" gap={1}>
                {t('Person 2')}
                <PersonMarkIcon role={person2Role} />
              </Box>
            </TableCell>
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
          <TableRow>
            <TableCell align="left">{t('Withdraw')}</TableCell>
            <TableCell align="center">
              <Button
                variant={
                  mark === 'person1_duplicate' ? 'contained' : 'outlined'
                }
                color="primary"
                fullWidth
                data-cy="button-na-withdraw-person1"
                onClick={() => withdraw('person1_duplicate', person1)}
              >
                {t('Withdraw')}
              </Button>
            </TableCell>
            <TableCell align="center">
              <Button
                variant={
                  mark === 'person2_duplicate' ? 'contained' : 'outlined'
                }
                color="primary"
                fullWidth
                data-cy="button-na-withdraw-person2"
                onClick={() => withdraw('person2_duplicate', person2)}
              >
                {t('Withdraw')}
              </Button>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align="center" colSpan={2}>
              <Button
                variant={mark === 'not_duplicates' ? 'contained' : 'outlined'}
                color="primary"
                fullWidth
                data-cy="button-na-not-duplicates"
                onClick={markNotDuplicates}
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
                disabled={!mark}
                data-cy="button-na-clear"
                onClick={onClear}
              >
                {t('Clear')}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
      {reassignments.length > 0 && (
        <Box mt={4} data-cy="na-reassign-section">
          <Typography variant="subtitle1">
            {t('Reassign roles before finalizing')}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {t(
              'The withdrawn individual holds a role that would leave their household without it.',
            )}
          </Typography>
          {reassignments.map((assignment) => {
            const key = reassignmentKey(
              assignment.role,
              assignment.household,
            );
            return (
              <Box
                key={key}
                mt={2}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                gap={2}
                data-cy={`na-reassign-row-${assignment.role}-${assignment.householdUnicefId}`}
              >
                <Typography variant="body2">
                  {t(roleLabel(assignment.role))} —{' '}
                  {assignment.householdUnicefId}
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <Typography
                    variant="body2"
                    color={
                      assignment.newIndividualName
                        ? 'textPrimary'
                        : 'textSecondary'
                    }
                  >
                    {assignment.newIndividualName ?? t('Not reassigned')}
                  </Typography>
                  <Button
                    variant="outlined"
                    color="primary"
                    size="small"
                    onClick={() => setOpenReassignKey(key)}
                    data-cy={`button-na-reassign-${assignment.role}`}
                  >
                    {assignment.newIndividual ? t('Change') : t('Select')}
                  </Button>
                </Box>
              </Box>
            );
          })}
        </Box>
      )}
      {openReassignment && duplicateIndividual && (
        <NaReassignRoleModal
          open
          onClose={() => setOpenReassignKey(null)}
          role={openReassignment.role}
          household={{
            id: openReassignment.household,
            unicefId: openReassignment.householdUnicefId,
          }}
          individualToReassign={duplicateIndividual}
          onSelect={(individual) => onReassign(openReassignKey, individual)}
        />
      )}
    </ApproveBox>
  );
};
