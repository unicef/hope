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
import { restQueryKey } from '@utils/queryKeys';
import { ReactElement, ReactNode, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ApproveBox,
  StyledTable,
} from '../GrievancesApproveSection/ApproveSectionStyles';
import { getGrievanceDetailsPath } from '../utils/createGrievanceUtils';
import { NaReassignRoleModal } from './NaReassignRoleModal';
import { applyMark, clearMark, individualRole } from './naDecision';
import { reassignmentKey, roleLabel } from './naRoleUtils';
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
  // Always-visible rows are the identity fields the operator needs to see even
  // when they match. The rest are only rendered when the two values differ.
  alwaysVisible?: boolean;
  // Rows that must never carry the "differs" highlight.
  neverHighlight?: boolean;
}

const familyNameOf = (i: any): string => i?.familyName ?? '';

const givenNameOf = (i: any): string => i?.givenName ?? '';

const addressOf = (i: any): string =>
  i?.household?.address ||
  i?.household?.village ||
  i?.household?.admin2?.name ||
  '';

const documentsOf = (i: any): string =>
  (i?.documents ?? [])
    .map((document) =>
      `${document?.type?.label ?? ''} ${document?.documentNumber ?? ''}`.trim(),
    )
    .filter(Boolean)
    .join(', ');

const accountsOf = (i: any): string =>
  (i?.accounts ?? [])
    .map((account) => `${account?.name ?? ''} ${account?.number ?? ''}`.trim())
    .filter(Boolean)
    .join(', ');

const comparisonRows: ComparisonRow[] = [
  {
    label: 'Last Name',
    render: (i) => familyNameOf(i) || '-',
    compare: familyNameOf,
    alwaysVisible: true,
  },
  {
    label: 'First Name',
    render: (i) => givenNameOf(i) || '-',
    compare: givenNameOf,
    alwaysVisible: true,
  },
  {
    label: 'Date of Birth',
    render: (i) => <UniversalMoment>{i?.birthDate}</UniversalMoment>,
    compare: (i) => i?.birthDate ?? '',
    alwaysVisible: true,
  },
  {
    label: 'Sex',
    render: (i) => i?.sex || '-',
    compare: (i) => i?.sex ?? '',
  },
  {
    label: 'Photo',
    render: (i) =>
      i?.id ? (
        <GrievanceIndividualPhotoModal
          individualId={i.id}
          programCode={i.programCode}
          isCurrent
        />
      ) : (
        '-'
      ),
    // Photos are expected to differ between two distinct individuals, so
    // don't apply the "differs" highlight to this row.
    compare: () => '',
    alwaysVisible: true,
    neverHighlight: true,
  },
  {
    label: 'Address',
    render: (i) => addressOf(i) || '-',
    compare: addressOf,
  },
  {
    label: 'Phone',
    render: (i) => i?.phoneNo || '-',
    compare: (i) => i?.phoneNo ?? '',
  },
  {
    label: 'Documents',
    render: (i) => documentsOf(i) || '-',
    compare: documentsOf,
  },
  {
    // Empty for users without POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION —
    // IndividualForNaComparisonSerializer.get_accounts gates the field server-side.
    label: 'Account',
    render: (i) => accountsOf(i) || '-',
    compare: accountsOf,
  },
];

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
  // Which possible duplicate is being compared against the golden record.
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    setActiveIndex(0);
    setOpenReassignKey(null);
  }, [ticketId]);

  const {
    data: ticket,
    isLoading,
    isError,
  } = useQuery<GrievanceTicketDetail>({
    queryKey: restQueryKey(RestService.restBusinessAreasGrievanceTicketsRetrieve, {
      businessAreaSlug,
      id: ticketId,
    }),
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

  if (isError) {
    return (
      <ApproveBox>
        <Typography variant="body2" color="error" data-cy="na-comparison-error">
          {t('Could not load this ticket. Please try again.')}
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
  // Older tickets carry a single `possibleDuplicate`; the multi-duplicate
  // version populates `possibleDuplicates`. Compare against every candidate.
  // `ticketDetails` is Record<string, any> in restgenerated, so the individuals
  // in it are untyped; NaIndividual only describes the role-reassignment slice.
  const candidates: any[] = (
    details?.possibleDuplicates?.length
      ? details.possibleDuplicates
      : [details?.possibleDuplicate]
  ).filter(Boolean);

  if (candidates.length === 0) {
    return (
      <ApproveBox>
        <Typography
          variant="body2"
          color="textSecondary"
          data-cy="na-comparison-no-duplicates"
        >
          {t('This ticket has no possible duplicate to compare.')}
        </Typography>
      </ApproveBox>
    );
  }

  const person2 = candidates[Math.min(activeIndex, candidates.length - 1)];
  const mark = person2?.id ? decision?.marks?.[person2.id] : undefined;

  // Withdrawing a person marks them duplicate and the other one distinct; any
  // HEAD/PRIMARY role they hold in a surviving household must be handed over
  // before this ticket can be executed.
  const withdraw = (newMark: NaMark): void =>
    onDecide(
      applyMark(decision, { person1, person2, mark: newMark }, candidates),
    );

  const markNotDuplicates = (): void =>
    onDecide(
      applyMark(
        decision,
        { person1, person2, mark: 'not_duplicates' },
        candidates,
      ),
    );

  const clearActiveMark = (): void => {
    const next = clearMark(decision, person1, person2?.id, candidates);
    if (next) {
      onDecide(next);
    } else {
      onClear();
    }
  };

  const reassignments: NaRoleAssignment[] = Object.values(
    decision?.reassignments ?? {},
  );
  const openReassignment = openReassignKey
    ? decision?.reassignments[openReassignKey]
    : undefined;
  // The reassignment list can span several pairs, so resolve the individual
  // losing the role from the assignment itself rather than from the active mark.
  const duplicateIndividual = openReassignment
    ? [person1, ...candidates].find(
        (individual) => individual?.id === openReassignment.individual,
      )
    : undefined;

  const similarity = person2?.similarityScore;

  // Ticket-wide, not per pair: person 1 is compared against every candidate, so a
  // mark made on one pair has to show on all of them.
  const person1Role = individualRole(decision, person1?.id);
  const person2Role = individualRole(decision, person2?.id);

  return (
    <ApproveBox>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6">
          {t('Ticket ID')}:{' '}
          {detailsPath ? (
            <BlackLink to={detailsPath}>
              <u>{ticket.unicefId}</u>
            </BlackLink>
          ) : (
            <u>{ticket.unicefId}</u>
          )}
        </Typography>
      </Box>
      {candidates.length > 1 && (
        <Box
          sx={{
            mb: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 3,
            px: 3,
            py: 2,
            bgcolor: '#f5f5f5',
            borderRadius: 2,
          }}
          data-cy="na-duplicate-selector"
        >
          <Button
            variant="outlined"
            size="medium"
            disabled={activeIndex === 0}
            onClick={() => setActiveIndex((index) => index - 1)}
            data-cy="button-na-duplicate-prev"
          >
            {t('Previous')}
          </Button>
          <Typography variant="h6" component="span">
            {t('Duplicate {{current}} of {{total}}', {
              current: activeIndex + 1,
              total: candidates.length,
            })}
          </Typography>
          <Button
            variant="outlined"
            size="medium"
            disabled={activeIndex >= candidates.length - 1}
            onClick={() => setActiveIndex((index) => index + 1)}
            data-cy="button-na-duplicate-next"
          >
            {t('Next')}
          </Button>
          <Typography variant="body1" color="textSecondary">
            {t('{{count}} of {{total}} decided', {
              count: candidates.filter(
                (candidate) => decision?.marks?.[candidate?.id],
              ).length,
              total: candidates.length,
            })}
          </Typography>
        </Box>
      )}
      <StyledTable data-cy="na-comparison-table">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell align="left">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('Person 1')}
                <PersonMarkIcon role={person1Role} />
              </Box>
            </TableCell>
            <TableCell align="left">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('Person 2')}
                <PersonMarkIcon role={person2Role} />
              </Box>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {comparisonRows.map((row) => {
            // A missing individual is not a difference — without both sides
            // every row would light up red.
            const differs =
              Boolean(person1) &&
              Boolean(person2) &&
              row.compare(person1) !== row.compare(person2);
            if (!row.alwaysVisible && !differs) return null;
            const highlight = differs && !row.neverHighlight;
            return (
              <TableRow
                key={row.label}
                data-cy={`na-comparison-row-${row.label}`}
                sx={
                  highlight ? { backgroundColor: DIFF_BACKGROUND } : undefined
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
              {typeof similarity === 'number' ? similarity : '-'}
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
                onClick={() => withdraw('person1_duplicate')}
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
                onClick={() => withdraw('person2_duplicate')}
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
                onClick={clearActiveMark}
              >
                {t('Clear')}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
      {reassignments.length > 0 && (
        <Box sx={{ mt: 4 }} data-cy="na-reassign-section">
          <Typography variant="subtitle1">
            {t('Reassign roles before finalizing')}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {t(
              'The withdrawn individual holds a role that would leave their household without it.',
            )}
          </Typography>
          {reassignments.map((assignment) => {
            const key = reassignmentKey(assignment.role, assignment.household);
            return (
              <Box
                key={key}
                sx={{
                  mt: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 2,
                }}
                data-cy={`na-reassign-row-${assignment.role}-${assignment.householdUnicefId}`}
              >
                <Typography variant="body2">
                  {t(roleLabel(assignment.role))} —{' '}
                  {assignment.householdUnicefId}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
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
