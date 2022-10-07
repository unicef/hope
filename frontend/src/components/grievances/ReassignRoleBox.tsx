import { Box, Paper, Typography } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';
import isEmpty from 'lodash/isEmpty';
import capitalize from 'lodash/capitalize';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../utils/constants';
import { GrievanceTicketNode } from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { LookUpReassignRole } from './LookUps/LookUpReassignRole/LookUpReassignRole';
import { ReassignRoleUnique } from './LookUps/LookUpReassignRole/ReassignRoleUnique';

const StyledBox = styled(Paper)`
  border: 1px solid ${({ theme }) => theme.hctPalette.oragne};
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const OrangeTitle = styled.div`
  color: ${({ theme }) => theme.hctPalette.oragne};
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
  ticket: GrievanceTicketNode;
  shouldDisplayButton?: boolean;
  shouldDisableButton?: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  let { individual } = ticket;
  let { household } = ticket;
  let reassignData;
  let uniqueIndividual;

  if (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
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
              href={`/${businessArea}/population/household/${el.household.id}`}
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
            individual={individual}
          />
        ) : null}
        {shouldDisplayButton &&
        ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
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

  return (
    <StyledBox>
      <OrangeTitle>
        <Typography variant='h6'>
          <WarnIcon />
          {t('Individual is the HOH or the external collector for a household')}
        </Typography>
      </OrangeTitle>
      <Typography variant='body2'>
        {t(
          'Upon removing you will need to select new individual(s) for this role.',
        )}
      </Typography>
      <Box mt={3} display='flex' flexDirection='column'>
        {shouldShowReassignHoH && (
          <Box mb={2} mt={2}>
            <Box mb={2}>
              <LabelizedField label={t('ROLE')}>
                <>{t('Head of Household')}</>
              </LabelizedField>
              <LabelizedField label={t('HOUSEHOLD ID')}>
                <ContentLink
                  href={`/${businessArea}/population/household/${ticket?.household.id}`}
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
                individual={individual}
              />
            ) : null}
          </Box>
        )}
        {mappedLookUpsForExternalHouseholds}
      </Box>
    </StyledBox>
  );
};
