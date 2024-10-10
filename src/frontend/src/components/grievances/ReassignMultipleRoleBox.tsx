import { Box, Paper, Typography } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import capitalize from 'lodash/capitalize';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  GrievanceTicketQuery,
  IndividualRoleInHouseholdRole,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { LookUpReassignRole } from './LookUps/LookUpReassignRole/LookUpReassignRole';

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

export function ReassignMultipleRoleBox({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const reassignData = JSON.parse(
    ticket.needsAdjudicationTicketDetails.roleReassignData,
  );
  const reassignDataDictByIndividualId = {};
  for (const key of Object.keys(reassignData)) {
    reassignDataDictByIndividualId[reassignData[key].individual] = reassignData[key];
  }
  const selectedIndividualsToReassign =
    ticket.needsAdjudicationTicketDetails.selectedDuplicates?.filter(
      (el) =>
        el.role === IndividualRoleInHouseholdRole.Primary || el.role === 'HEAD',
    );

  const mappedReassignLookups = (): React.ReactElement => (
    <>
      {selectedIndividualsToReassign.map((selectedIndividualToReassign) => {
        const { household } = selectedIndividualToReassign;

        const householdsAndRoles =
          selectedIndividualToReassign?.householdsAndRoles;

        const shouldShowReassignHoH =
          selectedIndividualToReassign?.id === household?.headOfHousehold?.id;

        const mappedLookUpsForExternalHouseholds = householdsAndRoles
          .filter((element) => element.role !== 'NO_ROLE')
          .map((householdAndRole) => (
            <Box mb={2} mt={2} key={householdAndRole.id}>
              <Box mb={2}>
                <LabelizedField label={t('ROLE')}>
                  <>{capitalize(householdAndRole.role)} Collector</>
                </LabelizedField>
                <LabelizedField label={t('INDIVIDUAL ID')}>
                  <ContentLink
                    href={`/${baseUrl}/population/individuals/${householdAndRole.individual.id}`}
                  >
                    {householdAndRole.individual.unicefId}
                  </ContentLink>{' '}
                  {householdAndRole.individual.fullName}
                </LabelizedField>
                <LabelizedField label={t('HOUSEHOLD ID')}>
                  <ContentLink
                    href={`/${baseUrl}/population/household/${householdAndRole.household.id}`}
                  >
                    {householdAndRole.household.unicefId}
                  </ContentLink>
                </LabelizedField>
              </Box>
              <LookUpReassignRole
                shouldDisableButton={false}
                individualRole={{
                  role: householdAndRole.role,
                  id: householdAndRole.id,
                }}
                ticket={ticket}
                household={householdAndRole.household}
                individualToReassign={selectedIndividualToReassign}
                initialSelectedIndividualId={reassignDataDictByIndividualId[selectedIndividualToReassign.id].new_individual}
              />
            </Box>
          ));

        return (
          <Box
            key={household.unicefId}
            mt={3}
            display="flex"
            flexDirection="column"
          >
            {shouldShowReassignHoH && (
              <Box mb={2} mt={2}>
                <Box mb={2}>
                  <LabelizedField label={t('ROLE')}>
                    <>{t('Head of Household')}</>
                  </LabelizedField>
                  <LabelizedField label={t('INDIVIDUAL ID')}>
                    <ContentLink
                      href={`/${baseUrl}/population/individuals/${ticket.individual.id}`}
                    >
                      {ticket.individual.unicefId}
                    </ContentLink>{' '}
                    {ticket.individual.fullName}
                  </LabelizedField>
                  <LabelizedField label={t('HOUSEHOLD ID')}>
                    <ContentLink
                      href={`/${baseUrl}/population/household/${ticket?.household.id}`}
                    >
                      {household.unicefId}
                    </ContentLink>
                  </LabelizedField>
                </Box>
                <LookUpReassignRole
                  shouldDisableButton={false}
                  individualRole={{ role: 'HEAD', id: 'HEAD' }}
                  ticket={ticket}
                  household={household}
                  individualToReassign={selectedIndividualToReassign}
                  initialSelectedIndividualId={reassignDataDictByIndividualId[selectedIndividualToReassign.id].new_individual}
                />
              </Box>
            )}
            {mappedLookUpsForExternalHouseholds}
          </Box>
        );
      })}
    </>
  );

  return selectedIndividualsToReassign.length ? (
    <StyledBox>
      <OrangeTitle>
        <Typography variant="h6">
          <WarnIcon />
          {t('Individual is the HOH or the collector for the household')}
        </Typography>
      </OrangeTitle>
      <Typography variant="body2">
        {t(
          'Upon changing you will need to select new individual(s) for this role.',
        )}
      </Typography>
      <Typography variant="body2">
        {t(
          'Upon removing you will need to select new individual(s) for this role.',
        )}
      </Typography>
      <Box mt={3} display="flex" flexDirection="column">
        {mappedReassignLookups()}
      </Box>
    </StyledBox>
  ) : null;
}
