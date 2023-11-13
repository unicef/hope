import {
  Box,
  Button,
  Checkbox,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import GroupIcon from '@material-ui/icons/Group';
import PersonIcon from '@material-ui/icons/Person';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveNeedsAdjudicationMutation,
} from '../../__generated__/graphql';
import { BlackLink } from '../core/BlackLink';
import { useConfirmation } from '../core/ConfirmationDialog';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';
import {
  ApproveBox,
  StyledTable,
} from './GrievancesApproveSection/ApproveSectionStyles';

export function NeedsAdjudicationDetailsNew({
  ticket,
  canApprove,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApprove: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const history = useHistory();
  const confirm = useConfirmation();
  const [approve] = useApproveNeedsAdjudicationMutation({
    refetchQueries: () => [
      {
        query: GrievanceTicketDocument,
        variables: { id: ticket.id },
      },
    ],
  });
  const details = ticket.needsAdjudicationTicketDetails;
  const initialIds = details.selectedIndividuals.map((el) => el.id);

  const [selectedDuplicates, setSelectedDuplicates] = useState(initialIds);
  const [isEditMode, setIsEditMode] = useState(false);

  const handleChecked = (id: string): void => {
    setSelectedDuplicates((prevSelected) =>
      prevSelected.includes(id)
        ? prevSelected.filter((el) => el !== id)
        : [...prevSelected, id],
    );
  };

  const allSelected = (): boolean => {
    const tableItemsCount =
      details.possibleDuplicates.length +
      (details.goldenRecordsIndividual?.id ? 1 : 0);
    return tableItemsCount === selectedDuplicates.length;
  };

  const getConfirmationText = (): string => {
    const singleRecordText =
      'Are you sure you want to mark this record as duplicate? It will be removed from Golden Records upon ticket closure.';
    const multipleRecordsText =
      'Are you sure you want to mark these records as duplicates? They will be removed from Golden Records upon ticket closure.';
    const allSelectedText = 'You cannot mark all individuals as duplicates';

    if (allSelected()) return t(allSelectedText);
    return t(
      selectedDuplicates.length > 1 ? multipleRecordsText : singleRecordText,
    );
  };

  const isApproved = !!details.selectedIndividual;
  const isEditable = isEditMode || !isApproved;

  const isApproveDisabled = (): boolean => {
    return (
      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
      !selectedDuplicates.length
    );
  };

  const findRecord = (itemId) => (record) => record.hitId === itemId;

  const getSimilarity = (records, individualId): number => {
    return records?.find(findRecord(individualId))?.score;
  };

  const getRecordSimilarity = (
    extraDataRecords,
    deduplicationRecords,
    individualId,
  ): number | string => {
    return (
      getSimilarity(extraDataRecords, individualId) ||
      getSimilarity(deduplicationRecords, individualId) ||
      '-'
    );
  };

  const getGoldenRecordSimilarity = (): number | string => {
    const { extraData, goldenRecordsIndividual, possibleDuplicate } = details;
    const individualId = possibleDuplicate?.id;
    return getRecordSimilarity(
      extraData?.goldenRecords,
      goldenRecordsIndividual?.deduplicationGoldenRecordResults,
      individualId,
    );
  };

  const getPossibleDuplicateSimilarity = (
    possibleDuplicate,
  ): number | string => {
    const { extraData, goldenRecordsIndividual } = details;
    const individualId = goldenRecordsIndividual?.id;
    return getRecordSimilarity(
      extraData?.possibleDuplicate,
      possibleDuplicate?.deduplicationGoldenRecordResults,
      individualId,
    );
  };

  const renderPossibleDuplicateRow = (
    possibleDuplicate,
    index,
  ): React.ReactElement => {
    return (
      <TableRow key={possibleDuplicate?.id}>
        <TableCell align='left'>
          <Checkbox
            color='primary'
            disabled={
              !isEditable ||
              ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
            }
            checked={selectedDuplicates.includes(possibleDuplicate?.id)}
            onChange={() => handleChecked(possibleDuplicate?.id)}
          />
        </TableCell>
        <TableCell align='left'>
          {/* //TODO: take uniqueness from the backend */}
          {index % 2 === 0 ? <GroupIcon /> : <PersonIcon />}
        </TableCell>
        <TableCell align='left'>
          <BlackLink
            to={`/${businessArea}/population/individuals/${possibleDuplicate?.id}`}
          >
            {possibleDuplicate?.unicefId}
          </BlackLink>
        </TableCell>
        <TableCell align='left'>
          <BlackLink
            to={`/${businessArea}/population/household/${possibleDuplicate?.household?.id}`}
          >
            {possibleDuplicate?.household?.unicefId || '-'}
          </BlackLink>
        </TableCell>
        <TableCell align='left'>{possibleDuplicate?.fullName}</TableCell>
        <TableCell align='left'>{possibleDuplicate?.sex}</TableCell>
        <TableCell align='left'>
          <UniversalMoment>{possibleDuplicate?.birthDate}</UniversalMoment>
        </TableCell>
        <TableCell align='left'>
          {getPossibleDuplicateSimilarity(possibleDuplicate)}
        </TableCell>
        <TableCell align='left'>
          <UniversalMoment>
            {possibleDuplicate?.lastRegistrationDate}
          </UniversalMoment>
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.documents?.edges[0]?.node.type.label}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.documents?.edges[0]?.node.documentNumber}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.household?.admin2?.name}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.household?.village}
        </TableCell>
      </TableRow>
    );
  };

  return (
    <ApproveBox>
      <Title>
        <Box display='flex' flexDirection='column'>
          <Typography variant='h6'>
            {t('Needs Adjudication Details')}
          </Typography>
          <Box gridGap={24} display='flex' mt={2}>
            <Button
              onClick={() =>
                history.push({
                  pathname: `/${businessArea}/grievance/new-ticket`,
                  state: { linkedTicketId: ticket.id },
                })
              }
              variant='outlined'
              color='primary'
              data-cy='button-create-linked-ticket'
            >
              {t('Create Linked Ticket')}
            </Button>
            {!isEditable && (
              <Button
                variant='outlined'
                color='primary'
                data-cy='button-edit'
                disabled={
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                onClick={() => setIsEditMode(true)}
              >
                {t('Edit')}
              </Button>
            )}
            {isEditable && canApprove && (
              <Button
                disabled={isApproveDisabled()}
                data-cy='button-mark-distinct'
                onClick={() =>
                  confirm({
                    content: getConfirmationText(),
                    disabled: allSelected(),
                  }).then(() => {
                    approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        selectedIndividualIds: selectedDuplicates,
                      },
                    });
                    setIsEditMode(false);
                  })
                }
                variant='contained'
                color='primary'
              >
                {t('Mark as Distinct')}
              </Button>
            )}
            {isEditable && canApprove && (
              <Button
                disabled={isApproveDisabled()}
                data-cy='button-mark-duplicate'
                onClick={() =>
                  confirm({
                    content: getConfirmationText(),
                    disabled: allSelected(),
                  }).then(() => {
                    approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        selectedIndividualIds: selectedDuplicates,
                      },
                    });
                    setIsEditMode(false);
                  })
                }
                variant='contained'
                color='primary'
              >
                {t('Mark as Duplicate')}
              </Button>
            )}
          </Box>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell data-cy='table-cell-uniqueness' align='left'>
              {t('Uniqueness')}
            </TableCell>
            <TableCell data-cy='table-cell-individual-id' align='left'>
              {t('Individual ID')}
            </TableCell>
            <TableCell data-cy='table-cell-household-id' align='left'>
              {t('Household ID')}
            </TableCell>
            <TableCell data-cy='table-cell-full-name' align='left'>
              {t('Full Name')}
            </TableCell>
            <TableCell data-cy='table-cell-gender' align='left'>
              {t('Gender')}
            </TableCell>
            <TableCell data-cy='table-cell-date-of-birth' align='left'>
              {t('Date of Birth')}
            </TableCell>
            <TableCell data-cy='table-cell-similarity-score' align='left'>
              {t('Similarity Score')}
            </TableCell>
            <TableCell data-cy='table-cell-last-registration-date' align='left'>
              {t('Last Registration Date')}
            </TableCell>
            <TableCell data-cy='table-cell-doc-type' align='left'>
              {t('Doc Type')}
            </TableCell>
            <TableCell data-cy='table-cell-doc-number' align='left'>
              {t('Doc #')}
            </TableCell>
            <TableCell data-cy='table-cell-admin-level2' align='left'>
              {t('Admin Level 2')}
            </TableCell>
            <TableCell data-cy='table-cell-village' align='left'>
              {t('Village')}
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>
              <Checkbox
                color='primary'
                data-cy='checkbox-individual'
                disabled={
                  !isEditable ||
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                checked={selectedDuplicates.includes(
                  details.goldenRecordsIndividual?.id,
                )}
                onChange={() =>
                  handleChecked(details.goldenRecordsIndividual?.id)
                }
              />
            </TableCell>
            <TableCell align='left'>
              {/* //TODO: take uniqueness from the backend */}
              <PersonIcon />
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                to={`/${businessArea}/population/individuals/${details.goldenRecordsIndividual?.id}`}
              >
                {details.goldenRecordsIndividual?.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                to={`/${businessArea}/population/household/${details.goldenRecordsIndividual?.household?.id}`}
              >
                {details.goldenRecordsIndividual?.household?.unicefId || '-'}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.fullName}
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.sex}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.goldenRecordsIndividual?.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>{getGoldenRecordSimilarity()}</TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.goldenRecordsIndividual?.lastRegistrationDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {
                details.goldenRecordsIndividual?.documents?.edges[0]?.node.type
                  .label
              }
            </TableCell>
            <TableCell align='left'>
              {
                details.goldenRecordsIndividual?.documents?.edges[0]?.node
                  .documentNumber
              }
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.household?.admin2?.name}
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.household?.village}
            </TableCell>
          </TableRow>
          {details.possibleDuplicates.map((el, index) =>
            renderPossibleDuplicateRow(el, index),
          )}
        </TableBody>
      </StyledTable>
    </ApproveBox>
  );
}
