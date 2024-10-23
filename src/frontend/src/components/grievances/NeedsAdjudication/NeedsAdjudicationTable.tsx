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
    <Tooltip data-cy='people-icon-tooltip' title="Marked as Duplicate" >
      <PeopleIcon data-cy="people-icon" color="primary" />
    </Tooltip>
  );

  const distinctTooltip = (
    <Tooltip data-cy='person-icon-tooltip' title="Marked as Distinct" >
      <PersonIcon data-cy="person-icon" color="primary" />
    </Tooltip>
  );

  const checkboxDisabled =
    !isEditable ||
    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
    !isActiveProgram;

  const renderPossibleDuplicateRow = (possibleDuplicate) => (
    <TableRow key={possibleDuplicate.id} data-cy={`possible-duplicate-row-${possibleDuplicate?.unicefId}`}>
      <TableCell align="left" data-cy="checkbox-cell">
        <Checkbox
          color="primary"
          disabled={checkboxDisabled}
          checked={selectedIndividualIds.includes(possibleDuplicate.id)}
          onChange={() => handleSelect(possibleDuplicate.id)}
          data-cy="select-checkbox"
        />
      </TableCell>
      <TableCell align="left" data-cy="distinct-duplicate-cell">
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
      <TableCell align="left" data-cy="individual-id-cell">
        {!isAllPrograms ? (
          <BlackLink
            to={`/${baseUrl}/population/individuals/${possibleDuplicate?.id}`}
            data-cy="individual-link"
          >
            {possibleDuplicate?.unicefId}
          </BlackLink>
        ) : (
          <span data-cy="individual-id">{possibleDuplicate?.unicefId}</span>
        )}
      </TableCell>
      <TableCell align="left" data-cy="household-id-cell">
        {!isAllPrograms ? (
          <BlackLink
            to={`/${baseUrl}/population/household/${possibleDuplicate?.household?.id}`}
            data-cy="household-link"
          >
            {possibleDuplicate?.household?.unicefId || '-'}
          </BlackLink>
        ) : (
          <span data-cy="household-id">
            {possibleDuplicate?.household?.unicefId || '-'}
          </span>
        )}
      </TableCell>
      <TableCell align="left" data-cy="full-name-cell">
        {possibleDuplicate?.fullName}
      </TableCell>
      <TableCell align="left" data-cy="sex-cell">
        {possibleDuplicate?.sex}
      </TableCell>
      <TableCell align="left" data-cy="birth-date-cell">
        <UniversalMoment>{possibleDuplicate?.birthDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left" data-cy="similarity-cell">
        {getPossibleDuplicateSimilarity(possibleDuplicate)}
      </TableCell>
      <TableCell align="left" data-cy="last-registration-date-cell">
        <UniversalMoment>
          {possibleDuplicate?.lastRegistrationDate}
        </UniversalMoment>
      </TableCell>
      <TableCell align="left" data-cy="document-type-cell">
        {possibleDuplicate?.documents?.edges[0]?.node.type.label}
      </TableCell>
      <TableCell align="left" data-cy="document-number-cell">
        {possibleDuplicate?.documents?.edges[0]?.node.documentNumber}
      </TableCell>
      <TableCell align="left" data-cy="admin2-name-cell">
        {possibleDuplicate?.household?.admin2?.name}
      </TableCell>
      <TableCell align="left" data-cy="village-cell">
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
              disabled={checkboxDisabled}
              data-cy="select-all-checkbox"
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
        <TableRow data-cy={`possible-duplicate-row-${details.goldenRecordsIndividual?.unicefId}`}>
          <TableCell align="left">
            <Checkbox
              color="primary"
              data-cy="checkbox-individual"
              disabled={checkboxDisabled}
              checked={selectedIndividualIds.includes(
                details.goldenRecordsIndividual?.id,
              )}
              onChange={() => handleSelect(details.goldenRecordsIndividual?.id)}
            />
          </TableCell>
          <TableCell align="left" data-cy="distinct-duplicate-golden-cell">
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
          <TableCell align="left" data-cy="individual-id-cell">
            {!isAllPrograms ? (
              <BlackLink
                to={`/${baseUrl}/population/individuals/${details.goldenRecordsIndividual?.id}`}
                data-cy="individual-link"
              >
                {details.goldenRecordsIndividual?.unicefId}
              </BlackLink>
            ) : (
              <span data-cy="individual-id">
                {details.goldenRecordsIndividual?.unicefId}
              </span>
            )}
          </TableCell>
          <TableCell align="left" data-cy="household-id-cell">
            {!isAllPrograms ? (
              <BlackLink
                to={`/${baseUrl}/population/household/${details.goldenRecordsIndividual?.household?.id}`}
                data-cy="household-link"
              >
                {details.goldenRecordsIndividual?.household?.unicefId || '-'}
              </BlackLink>
            ) : (
              <span data-cy="household-id">
                {details.goldenRecordsIndividual?.household?.unicefId || '-'}
              </span>
            )}
          </TableCell>
          <TableCell align="left" data-cy="full-name-cell">
            {details.goldenRecordsIndividual?.fullName}
          </TableCell>
          <TableCell align="left" data-cy="gender-cell">
            {details.goldenRecordsIndividual?.sex}
          </TableCell>
          <TableCell align="left" data-cy="birth-date-cell">
            <UniversalMoment>
              {details.goldenRecordsIndividual?.birthDate}
            </UniversalMoment>
          </TableCell>
          <TableCell align="left" data-cy="similarity-score-cell">
            {getGoldenRecordSimilarity()}
          </TableCell>
          <TableCell align="left" data-cy="last-registration-date-cell">
            <UniversalMoment>
              {details.goldenRecordsIndividual?.lastRegistrationDate}
            </UniversalMoment>
          </TableCell>
          <TableCell align="left" data-cy="doc-type-cell">
            {
              details.goldenRecordsIndividual?.documents?.edges[0]?.node.type
                .label
            }
          </TableCell>
          <TableCell align="left" data-cy="doc-number-cell">
            {
              details.goldenRecordsIndividual?.documents?.edges[0]?.node
                .documentNumber
            }
          </TableCell>
          <TableCell align="left" data-cy="admin-level2-cell">
            {details.goldenRecordsIndividual?.household?.admin2?.name}
          </TableCell>
          <TableCell align="left" data-cy="village-cell">
            {details.goldenRecordsIndividual?.household?.village}
          </TableCell>
        </TableRow>
        {details.possibleDuplicates.map((el) => renderPossibleDuplicateRow(el))}
      </TableBody>
    </StyledTable>
  );
};
