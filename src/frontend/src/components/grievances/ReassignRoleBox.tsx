import { Box, Paper, Typography } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import capitalize from 'lodash/capitalize';
import isEmpty from 'lodash/isEmpty';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GrievanceTicketQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { LookUpReassignRole } from './LookUps/LookUpReassignRole/LookUpReassignRole';
import { ReassignRoleUnique } from './LookUps/LookUpReassignRole/ReassignRoleUnique';

const StyledBox = styled(Paper)`
  border: 1px solid ${({ theme }) => theme.hctPalette.orange};
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const OrangeTitle = styled.div`
  color: ${({ theme }) => theme.hctPalette.orange};
`;

const WarnIcon = styled(WarningIcon)`
  position: relative;
  top: 5px;
  margin-right: 10px;
`;

export const ReassignRoleBox = ({
  ticket,
  shouldDisplayButton,
  shouldDisableButton,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  shouldDisplayButton?: boolean;
  shouldDisableButton?: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  let { individual } = ticket;
  let { household } = ticket;
  let reassignData;
  let uniqueIndividual;

  if (ticket.category.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION) {
    individual = ticket.needsAdjudicationTicketDetails.selectedIndividual;
    household =
      ticket.needsAdjudicationTicketDetails.selectedIndividual?.household;
    reassignData = JSON.parse(
      ticket.needsAdjudicationTicketDetails.roleReassignData,
    );
    uniqueIndividual =
      ticket.needsAdjudicationTicketDetails.possibleDuplicate.id ===
      individual.id
        ? ticket.needsAdjudicationTicketDetails.goldenRecordsIndividual
        : ticket.needsAdjudicationTicketDetails.possibleDuplicate;
  } else if (
    ticket.category.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING
  ) {
    reassignData = JSON.parse(
      ticket.systemFlaggingTicketDetails.roleReassignData,
    );
  }
  let householdsAndRoles = individual?.householdsAndRoles;
  let shouldShowReassignHoH = individual?.id === household?.headOfHousehold?.id;

  if (
    ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
    ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
  ) {
    if (isEmpty(ticket.individualDataUpdateTicketDetails.individualData.role)) {
      householdsAndRoles = [];
    }
    if (
      isEmpty(
        ticket.individualDataUpdateTicketDetails.individualData.relationship,
      )
    ) {
      shouldShowReassignHoH = false;
    }
  }
  const reassignDataDictByIndividualId = {};
  for (const key of Object.keys(reassignData)) {
    reassignDataDictByIndividualId[reassignData[key].individual] = reassignData[key];
  }
  const mappedLookUpsForExternalHouseholds = householdsAndRoles
    .filter((el) => el.role !== 'NO_ROLE')
    .map((el) => (
      <Box mb={2} mt={2} key={el.id}>
        <Box mb={2}>
          <LabelizedField label={t('ROLE')}>
            <>{capitalize(el.role)} Collector</>
          </LabelizedField>
          <LabelizedField label={t('HOUSEHOLD ID')}>
            <ContentLink
              href={`/${baseUrl}/population/household/${el.household.id}`}
            >
              {el.household.unicefId}
            </ContentLink>
          </LabelizedField>
        </Box>
        {shouldDisplayButton ? (
          <LookUpReassignRole
            shouldDisableButton={shouldDisableButton}
            individualRole={{ role: el.role, id: el.id }}
            ticket={ticket}
            household={el.household}
            individualToReassign={individual}
            initialSelectedIndividualId={
              reassignDataDictByIndividualId[individual.id]?.new_individual
            }
          />
        ) : null}
        {shouldDisplayButton &&
        ticket.category.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION &&
        reassignData[el.id]?.individual !== uniqueIndividual.id ? (
          <ReassignRoleUnique
            individualRole={{ role: el.role, id: el.id }}
            ticket={ticket}
            household={el.household}
            individual={uniqueIndividual}
          />
          ) : null}
      </Box>
    ));

  const showMessage = (): React.ReactElement => {
    if (
      (ticket.issueType.toString() ===
        GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL &&
        (ticket.individual?.role === 'PRIMARY' ||
          ticket.individual?.relationship === 'HEAD')) ||
      (ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL &&
        ticket.individualDataUpdateTicketDetails?.individualData?.role
          ?.previous_value === 'PRIMARY' &&
        (ticket.individualDataUpdateTicketDetails?.individualData?.role
          ?.value === 'ALTERNATE' ||
          ticket.individualDataUpdateTicketDetails?.individualData?.role
            ?.value === 'NO_ROLE'))
    ) {
      return (
        <Typography variant='body2'>
          {t(
            'Upon removing you will need to select new individual(s) for this role.',
          )}
        </Typography>
      );
    }
    return null;
  };

  return (
    <StyledBox>
      <OrangeTitle>
        <Typography variant="h6">
          <WarnIcon />
          {t('Individual is the HOH or the collector for the household')}
        </Typography>
      </OrangeTitle>
      {showMessage()}
      <Box mt={3} display="flex" flexDirection="column">
        {shouldShowReassignHoH && (
          <Box mb={2} mt={2}>
            <Box mb={2}>
              <LabelizedField label={t('ROLE')}>
                <>{t('Head of Household')}</>
              </LabelizedField>
              <LabelizedField label={t('HOUSEHOLD ID')}>
                <ContentLink
                  href={`/${baseUrl}/population/household/${ticket?.household.id}`}
                >
                  {household.unicefId}
                </ContentLink>
              </LabelizedField>
            </Box>
            {shouldDisplayButton ? (
              <LookUpReassignRole
                shouldDisableButton={shouldDisableButton}
                individualRole={{ role: 'HEAD', id: 'HEAD' }}
                ticket={ticket}
                household={household}
                individualToReassign={individual}
                initialSelectedIndividualId={
                  reassignDataDictByIndividualId[individual.id]?.new_individual
                }
              />
            ) : null}
          </Box>
        )}
        {mappedLookUpsForExternalHouseholds}
      </Box>
    </StyledBox>
  );
};
