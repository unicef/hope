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
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveNeedsAdjudicationMutation,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { BlackLink } from '../core/BlackLink';
import { useConfirmation } from '../core/ConfirmationDialog';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';
import {
  ApproveBox,
  StyledTable,
} from './GrievancesApproveSection/ApproveSectionStyles';

export function NeedsAdjudicationDetailsOld({
  ticket,
  canApprove,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApprove: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
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
  const [selectedDuplicate, setSelectedDuplicate] = useState(
    details?.selectedIndividual?.id,
  );
  const [isEditMode, setIsEditMode] = useState(false);
  const confirmationText = t(
    'Are you sure you want to mark this record as duplicate? It will be removed from Golden Records upon ticket closure.',
  );
  const isApproved = !!details.selectedIndividual;
  const isEditable = isEditMode || !isApproved;

  const isApproveDisabled = (): boolean => {
    return (
      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
      !selectedDuplicate
    );
  };

  const findRecord = (itemId) => (record) => record.hitId === itemId;

  const getSimilarity = (records, individualId): number => {
    return records?.find(findRecord(individualId))?.score;
  };

  const getGoldenRecordSimilarity = (): number | string => {
    const { extraData, goldenRecordsIndividual, possibleDuplicate } = details;
    const individualId = possibleDuplicate?.id;
    const extraDataGoldenRecords = extraData?.goldenRecords;
    const deduplicationGoldenRecordResults =
      goldenRecordsIndividual?.deduplicationGoldenRecordResults;

    return (
      getSimilarity(extraDataGoldenRecords, individualId) ||
      getSimilarity(deduplicationGoldenRecordResults, individualId) ||
      '-'
    );
  };

  const getPossibleDuplicateSimilarity = (): number | string => {
    const { extraData, goldenRecordsIndividual, possibleDuplicate } = details;
    const individualId = goldenRecordsIndividual?.id;
    const extraDataPossibleDuplicate1 = extraData?.possibleDuplicate;
    const deduplicationGoldenRecordResults =
      possibleDuplicate?.deduplicationGoldenRecordResults;

    return (
      getSimilarity(extraDataPossibleDuplicate1, individualId) ||
      getSimilarity(deduplicationGoldenRecordResults, individualId) ||
      '-'
    );
  };

  return (
    <ApproveBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t('Needs Adjudication Details')}
          </Typography>
          <Box gridGap={24} display='flex'>
            <Button
              onClick={() =>
                history.push({
                  pathname: `/${baseUrl}/grievance/new-ticket`,
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
                data-cy='button-mark-duplicate'
                onClick={() =>
                  confirm({
                    content: confirmationText,
                  }).then(() => {
                    approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        selectedIndividualId: selectedDuplicate,
                      },
                    });
                    setIsEditMode(false);
                  })
                }
                variant='outlined'
                color='primary'
              >
                {t('Mark Duplicate')}
              </Button>
            )}
          </Box>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
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
                checked={
                  selectedDuplicate === details.goldenRecordsIndividual?.id
                }
                onChange={(event, checked) =>
                  setSelectedDuplicate(
                    checked ? details.goldenRecordsIndividual?.id : null,
                  )
                }
              />
            </TableCell>

            <TableCell align='left'>
              <BlackLink
                to={`/${baseUrl}/population/individuals/${details.goldenRecordsIndividual?.id}`}
              >
                {details.goldenRecordsIndividual?.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                to={`/${baseUrl}/population/household/${details.goldenRecordsIndividual?.household?.id}`}
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
          <TableRow>
            <TableCell align='left'>
              <Checkbox
                color='primary'
                disabled={
                  !isEditable ||
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                checked={selectedDuplicate === details.possibleDuplicate?.id}
                onChange={(event, checked) =>
                  setSelectedDuplicate(
                    checked ? details.possibleDuplicate?.id : null,
                  )
                }
              />
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                to={`/${baseUrl}/population/individuals/${details.possibleDuplicate?.id}`}
              >
                {details.possibleDuplicate?.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                to={`/${baseUrl}/population/household/${details.possibleDuplicate?.household?.id}`}
              >
                {details.possibleDuplicate?.household?.unicefId || '-'}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.fullName}
            </TableCell>
            <TableCell align='left'>{details.possibleDuplicate?.sex}</TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.possibleDuplicate?.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {getPossibleDuplicateSimilarity()}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.possibleDuplicate?.lastRegistrationDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.documents?.edges[0]?.node.type.label}
            </TableCell>
            <TableCell align='left'>
              {
                details.possibleDuplicate?.documents?.edges[0]?.node
                  .documentNumber
              }
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.household?.admin2?.name}
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.household?.village}
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </ApproveBox>
  );
}
