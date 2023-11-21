import { Box, Grid, Typography } from '@material-ui/core';
import InfoIcon from '@material-ui/icons/Info';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  GrievanceTicketQuery,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { choicesToDict } from '../../utils/utils';
import { BlackLink } from '../core/BlackLink';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { LoadingComponent } from '../core/LoadingComponent';
import { Title } from '../core/Title';
import { ApproveDeleteHouseholdGrievanceDetails } from './ApproveDeleteHouseholdGrievanceDetails';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';

const Info = styled(InfoIcon)`
  color: ${({ theme }) => theme.hctPalette.gray};
  margin-right: 10px;
`;

export const DeleteHouseholdGrievanceDetails = ({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (choicesLoading) return <LoadingComponent />;
  if (!choicesData) return null;

  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );

  const { approveStatus } = ticket.deleteHouseholdTicketDetails;

  return (
    <ApproveBox>
      <Title>
        <Box display='flex' justifyContent='space-between' alignItems='center'>
          <Typography variant='h6'>{t('Household to be withdrawn')}</Typography>
          {approveStatus &&
            ticket.deleteHouseholdTicketDetails.reasonHousehold && (
              <Box display='flex' alignItems='center'>
                <Info />
                <Box mr={2}>
                  <p>This household is a duplicate of a household ID:</p>
                </Box>
                <BlackLink
                  to={`/${baseUrl}/population/household/${ticket.deleteHouseholdTicketDetails.reasonHousehold.id}`}
                >
                  {ticket.deleteHouseholdTicketDetails.reasonHousehold.unicefId}
                </BlackLink>
                {canApproveDataChange && (
                  <ApproveDeleteHouseholdGrievanceDetails
                    type='edit'
                    ticket={ticket}
                  />
                )}
              </Box>
            )}
          {canApproveDataChange && (
            <ApproveDeleteHouseholdGrievanceDetails
              type='button'
              ticket={ticket}
            />
          )}
        </Box>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={3}>
          <LabelizedField label={t('Household Size')}>
            {ticket.household.size}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Residence Status')}>
            {residenceChoicesDict[ticket.household.residenceStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Head of Household')}>
            <ContentLink
              href={`/${baseUrl}/population/individuals/${ticket.household.headOfHousehold.id}`}
            >
              {ticket.household.headOfHousehold.fullName}
            </ContentLink>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Country')}>
            {ticket.household.country}
          </LabelizedField>
        </Grid>

        <Grid item xs={3}>
          <LabelizedField label={t('Country of Origin')}>
            {ticket.household.countryOrigin}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Address')}>
            {ticket.household.address}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Village')}>
            {ticket.household.village}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 1')}>
            {ticket.household.admin1?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 2')}>
            {ticket.household.admin2?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Geolocation')}>
            {ticket.household.geopoint
              ? `${ticket.household.geopoint.coordinates[0]}, ${ticket.household.geopoint.coordinates[1]}`
              : '-'}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('UNHCR CASE ID')}>
            {ticket.household?.unhcrId}
          </LabelizedField>
        </Grid>
      </Grid>
    </ApproveBox>
  );
};
