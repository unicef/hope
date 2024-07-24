import React from 'react';
import { BlackLink } from '@core/BlackLink';
import { UniversalMoment } from '@core/UniversalMoment';
import PeopleIcon from '@mui/icons-material/People';
import PersonIcon from '@mui/icons-material/Person';
import {
  Checkbox,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
} from '@mui/material';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { StyledTable } from '../GrievancesApproveSection/ApproveSectionStyles';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { GrievanceTicketQuery } from '@generated/graphql';

interface NeedsAdjudicationTableProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  isEditable: boolean;
  selectedIndividualIds: string[];
  setSelectedIndividualIds: (
    ids: ((prevSelected: string[]) => string[]) | string[],
  ) => void;
  getGoldenRecordSimilarity: () => number | string;
  getPossibleDuplicateSimilarity: (possibleDuplicate: any) => string | number;
  markedDistinctInPossibleDuplicates: string[];
  markedDuplicateInPossibleDuplicates: string[];
}

export const NeedsAdjudicationTable = ({
  ticket,
  isEditable,
  selectedIndividualIds,
  setSelectedIndividualIds,
  getGoldenRecordSimilarity,
  getPossibleDuplicateSimilarity,
  markedDistinctInPossibleDuplicates,
  markedDuplicateInPossibleDuplicates,
}: NeedsAdjudicationTableProps) => {
  const { t } = useTranslation();
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();
  const details = ticket?.needsAdjudicationTicketDetails;

  const handleSelect = (id: string) => {
    setSelectedIndividualIds((prevSelected: string[]) => {
      if (prevSelected.includes(id)) {
        return prevSelected.filter((el: string) => el !== id);
      } else {
        return [...prevSelected, id];
      }
    });
  };

  const getAllIds = () => {
    const allIds = [
      ...details.possibleDuplicates.map((duplicate) => duplicate.id),
    ];
    if (details.goldenRecordsIndividual) {
      allIds.push(details.goldenRecordsIndividual.id);
    }
    return allIds;
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedIndividualIds(getAllIds());
    } else {
      setSelectedIndividualIds([]);
    }
  };

  const isAllSelected = (): boolean => {
    const allIds = getAllIds();
    return allIds.every((id) => selectedIndividualIds.includes(id));
  };

  const duplicateTooltip = (
    <Tooltip title="Marked as Duplicate">
      <PeopleIcon color="primary" />
    </Tooltip>
  );

  const distinctTooltip = (
    <Tooltip title="Marked as Distinct">
      <PersonIcon color="secondary" />
    </Tooltip>
  );
  const renderPossibleDuplicateRow = (possibleDuplicate) => (
    <TableRow key={possibleDuplicate?.id}>
      <TableCell align="left">
        <Checkbox
          color="primary"
          disabled={
            !isEditable ||
            ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
            !isActiveProgram
          }
          checked={selectedIndividualIds.includes(possibleDuplicate.id)}
          onChange={() => handleSelect(possibleDuplicate.id)}
        />
      </TableCell>
      <TableCell align="left">
        {(() => {
          const { id } = possibleDuplicate;

          if (markedDistinctInPossibleDuplicates.includes(id)) {
            return distinctTooltip;
          }

          if (markedDuplicateInPossibleDuplicates.includes(id)) {
            return duplicateTooltip;
          }

          return '-';
        })()}
      </TableCell>
      <TableCell align="left">
        {!isAllPrograms ? (
          <BlackLink
            to={`/${baseUrl}/population/individuals/${possibleDuplicate?.id}`}
          >
            {possibleDuplicate?.unicefId}
          </BlackLink>
        ) : (
          <span>{possibleDuplicate?.unicefId}</span>
        )}
      </TableCell>
      <TableCell align="left">
        {!isAllPrograms ? (
          <BlackLink
            to={`/${baseUrl}/population/household/${possibleDuplicate?.household?.id}`}
          >
            {possibleDuplicate?.household?.unicefId || '-'}
          </BlackLink>
        ) : (
          <span>{possibleDuplicate?.household?.unicefId || '-'}</span>
        )}
      </TableCell>
      <TableCell align="left">{possibleDuplicate?.fullName}</TableCell>
      <TableCell align="left">{possibleDuplicate?.sex}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{possibleDuplicate?.birthDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        {getPossibleDuplicateSimilarity(possibleDuplicate)}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>
          {possibleDuplicate?.lastRegistrationDate}
        </UniversalMoment>
      </TableCell>
      <TableCell align="left">
        {possibleDuplicate?.documents?.edges[0]?.node.type.label}
      </TableCell>
      <TableCell align="left">
        {possibleDuplicate?.documents?.edges[0]?.node.documentNumber}
      </TableCell>
      <TableCell align="left">
        {possibleDuplicate?.household?.admin2?.name}
      </TableCell>
      <TableCell align="left">
        {possibleDuplicate?.household?.village}
      </TableCell>
    </TableRow>
  );

  return (
    <StyledTable>
      <TableHead>
        <TableRow>
          <TableCell align="left">
            <Checkbox
              indeterminate={selectedIndividualIds.length > 0 && !isAllSelected}
              checked={isAllSelected()}
              onChange={handleSelectAll}
              disabled={!isEditable}
            />
          </TableCell>
          <TableCell data-cy="table-cell-uniqueness" align="left">
            {t('Uniqueness')}
          </TableCell>
          <TableCell data-cy="table-cell-individual-id" align="left">
            {t('Individual ID')}
          </TableCell>
          <TableCell data-cy="table-cell-household-id" align="left">
            {t('Household ID')}
          </TableCell>
          <TableCell data-cy="table-cell-full-name" align="left">
            {t('Full Name')}
          </TableCell>
          <TableCell data-cy="table-cell-gender" align="left">
            {t('Gender')}
          </TableCell>
          <TableCell data-cy="table-cell-date-of-birth" align="left">
            {t('Date of Birth')}
          </TableCell>
          <TableCell data-cy="table-cell-similarity-score" align="left">
            {t('Similarity Score')}
          </TableCell>
          <TableCell data-cy="table-cell-last-registration-date" align="left">
            {t('Last Registration Date')}
          </TableCell>
          <TableCell data-cy="table-cell-doc-type" align="left">
            {t('Doc Type')}
          </TableCell>
          <TableCell data-cy="table-cell-doc-number" align="left">
            {t('Doc #')}
          </TableCell>
          <TableCell data-cy="table-cell-admin-level2" align="left">
            {t('Admin Level 2')}
          </TableCell>
          <TableCell data-cy="table-cell-village" align="left">
            {t('Village')}
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        <TableRow>
          <TableCell align="left">
            <Checkbox
              color="primary"
              data-cy="checkbox-individual"
              disabled={
                !isEditable ||
                ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
                !isActiveProgram
              }
              checked={selectedIndividualIds.includes(
                details.goldenRecordsIndividual?.id,
              )}
              onChange={() => handleSelect(details.goldenRecordsIndividual?.id)}
            />
          </TableCell>
          <TableCell align="left">
            {details.goldenRecordsIndividual
              ? (() => {
                  const id = details.goldenRecordsIndividual.id;

                  if (markedDistinctInPossibleDuplicates.includes(id)) {
                    return distinctTooltip;
                  }

                  if (markedDuplicateInPossibleDuplicates.includes(id)) {
                    return duplicateTooltip;
                  }

                  return '-';
                })()
              : '-'}
          </TableCell>
          <TableCell align="left">
            {!isAllPrograms ? (
              <BlackLink
                to={`/${baseUrl}/population/individuals/${details.goldenRecordsIndividual?.id}`}
              >
                {details.goldenRecordsIndividual?.unicefId}
              </BlackLink>
            ) : (
              <span>{details.goldenRecordsIndividual?.unicefId}</span>
            )}
          </TableCell>
          <TableCell align="left">
            {!isAllPrograms ? (
              <BlackLink
                to={`/${baseUrl}/population/household/${details.goldenRecordsIndividual?.household?.id}`}
              >
                {details.goldenRecordsIndividual?.household?.unicefId || '-'}
              </BlackLink>
            ) : (
              <span>
                {details.goldenRecordsIndividual?.household?.unicefId || '-'}
              </span>
            )}
          </TableCell>
          <TableCell align="left">
            {details.goldenRecordsIndividual?.fullName}
          </TableCell>
          <TableCell align="left">
            {details.goldenRecordsIndividual?.sex}
          </TableCell>
          <TableCell align="left">
            <UniversalMoment>
              {details.goldenRecordsIndividual?.birthDate}
            </UniversalMoment>
          </TableCell>
          <TableCell align="left">{getGoldenRecordSimilarity()}</TableCell>
          <TableCell align="left">
            <UniversalMoment>
              {details.goldenRecordsIndividual?.lastRegistrationDate}
            </UniversalMoment>
          </TableCell>
          <TableCell align="left">
            {
              details.goldenRecordsIndividual?.documents?.edges[0]?.node.type
                .label
            }
          </TableCell>
          <TableCell align="left">
            {
              details.goldenRecordsIndividual?.documents?.edges[0]?.node
                .documentNumber
            }
          </TableCell>
          <TableCell align="left">
            {details.goldenRecordsIndividual?.household?.admin2?.name}
          </TableCell>
          <TableCell align="left">
            {details.goldenRecordsIndividual?.household?.village}
          </TableCell>
        </TableRow>
        {details.possibleDuplicates.map((el) => renderPossibleDuplicateRow(el))}
      </TableBody>
    </StyledTable>
  );
};
