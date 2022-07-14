import { Box, Paper, Typography } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';
import capitalize from 'lodash/capitalize';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  GrievanceTicketQuery,
  IndividualRoleInHouseholdRole,
} from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { LookUpReassignRole } from './LookUps/LookUpReassignRole/LookUpReassignRole';

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

export const ReassignMultipleRoleBox = ({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const selectedIndividualsToReassign = ticket.needsAdjudicationTicketDetails.selectedIndividuals?.filter(
    (el) =>
      el.role === IndividualRoleInHouseholdRole.Primary || el.role === 'HEAD',
  );

  const mappedReassignLookups = (): React.ReactElement => {
    return (
      <>
        {selectedIndividualsToReassign.map((selectedIndividualToReassign) => {
          const { household } = selectedIndividualToReassign;

          const householdsAndRoles =
            selectedIndividualToReassign?.householdsAndRoles;

          const shouldShowReassignHoH =
            selectedIndividualToReassign?.id === household?.headOfHousehold?.id;

          const mappedLookUpsForExternalHouseholds = householdsAndRoles
            .filter((element) => element.role !== 'NO_ROLE')
            .map((householdAndRole) => {
              return (
                <Box mb={2} mt={2} key={householdAndRole.id}>
                  <Box mb={2}>
                    <LabelizedField label={t('ROLE')}>
                      <>{capitalize(householdAndRole.role)} Collector</>
                    </LabelizedField>
                    <LabelizedField label={t('INDIVIDUAL ID')}>
                      <ContentLink
                        href={`/${businessArea}/population/individuals/${householdAndRole.individual.id}`}
                      >
                        {householdAndRole.individual.unicefId}
                      </ContentLink>{' '}
                      {householdAndRole.individual.fullName}
                    </LabelizedField>
                    <LabelizedField label={t('HOUSEHOLD ID')}>
                      <ContentLink
                        href={`/${businessArea}/population/household/${householdAndRole.household.id}`}
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
                    individual={selectedIndividualToReassign}
                  />
                </Box>
              );
            });

          return (
            <Box
              key={household.unicefId}
              mt={3}
              display='flex'
              flexDirection='column'
            >
              {shouldShowReassignHoH && (
                <Box mb={2} mt={2}>
                  <Box mb={2}>
                    <LabelizedField label={t('ROLE')}>
                      <>{t('Head of Household')}</>
                    </LabelizedField>
                    <LabelizedField label={t('INDIVIDUAL ID')}>
                      <ContentLink
                        href={`/${businessArea}/population/individuals/${ticket.individual.id}`}
                      >
                        {ticket.individual.unicefId}
                      </ContentLink>{' '}
                      {ticket.individual.fullName}
                    </LabelizedField>
                    <LabelizedField label={t('HOUSEHOLD ID')}>
                      <ContentLink
                        href={`/${businessArea}/population/household/${ticket?.household.id}`}
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
                    individual={selectedIndividualToReassign}
                  />
                </Box>
              )}
              {mappedLookUpsForExternalHouseholds}
            </Box>
          );
        })}
      </>
    );
  };

  return selectedIndividualsToReassign.length ? (
    <>
      <StyledBox>
        <OrangeTitle>
          <Typography variant='h6'>
            <WarnIcon />
            {t(
              'Individual is the HOH or the external collector for a household',
            )}
          </Typography>
        </OrangeTitle>
        <Typography variant='body2'>
          {t(
            'Upon removing you will need to select new individual(s) for this role.',
          )}
        </Typography>
        <Box mt={3} display='flex' flexDirection='column'>
          {mappedReassignLookups()}
        </Box>
      </StyledBox>
    </>
  ) : null;
};
