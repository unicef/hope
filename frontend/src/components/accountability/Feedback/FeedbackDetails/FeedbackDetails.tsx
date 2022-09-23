import { Grid, GridSize, Typography } from '@material-ui/core';
import { Title } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { reduceChoices, renderUserName } from '../../../../utils/utils';
import {
  GrievanceTicketQuery,
  GrievancesChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { ContentLink } from '../../../core/ContentLink';
import { LabelizedField } from '../../../core/LabelizedField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { UniversalMoment } from '../../../core/UniversalMoment';

interface FeedbackDetailsProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  choicesData: GrievancesChoiceDataQuery;
  businessArea: string;
  canViewHouseholdDetails: boolean;
  canViewIndividualDetails: boolean;
}

export const FeedbackDetails = ({
  ticket,
  choicesData,
  businessArea,
  canViewHouseholdDetails,
  canViewIndividualDetails,
}: FeedbackDetailsProps): React.ReactElement => {
  const { t } = useTranslation();

  const issueType = ticket.issueType
    ? choicesData.grievanceTicketIssueTypeChoices
        .filter((el) => el.category === ticket.category.toString())[0]
        .subCategories.filter(
          (el) => el.value === ticket.issueType.toString(),
        )[0].name
    : '-';

  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            {[
              {
                label: t('Category'),
                value: <span>{t('Feedback')}</span>,
                size: 3,
              },
              {
                label: t('Issue Type'),
                value: <span>{issueType}</span>,
                size: 3,
              },
              {
                label: t('Household ID'),
                value: (
                  <span>
                    {ticket.household?.id ? (
                      <ContentLink
                        href={
                          canViewHouseholdDetails
                            ? `/${businessArea}/population/household/${ticket.household.id}`
                            : undefined
                        }
                      >
                        {ticket.household.unicefId}
                      </ContentLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Individual ID'),
                value: (
                  <span>
                    {ticket.individual?.id ? (
                      <ContentLink
                        href={
                          canViewIndividualDetails
                            ? `/${businessArea}/population/individuals/${ticket.individual.id}`
                            : undefined
                        }
                      >
                        {ticket.individual.unicefId}
                      </ContentLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Programme'),
                value: ticket.programme?.name,
                size: 3,
              },
              {
                label: t('Created By'),
                value: renderUserName(ticket.createdBy),
                size: 3,
              },
              {
                label: t('Date Created'),
                value: <UniversalMoment>{ticket.createdAt}</UniversalMoment>,
                size: 3,
              },
              {
                label: t('Last Modified Date'),
                value: <UniversalMoment>{ticket.updatedAt}</UniversalMoment>,
                size: 3,
              },
              {
                label: t('Administrative Level 2'),
                value: ticket.admin,
                size: 3,
              },
              {
                label: t('Area / Village / Pay point'),
                value: ticket.area,
                size: 3,
              },
              {
                label: t('Languages Spoken'),
                value: ticket.language,
                size: 3,
              },
              {
                label: t('Description'),
                value: ticket.description,
                size: 12,
              },
              {
                label: t('Comments'),
                value: ticket.comments,
                size: 12,
              },
            ]
              .filter((el) => el)
              .map((el) => (
                <Grid key={el.label} item xs={el.size as GridSize}>
                  <LabelizedField label={el.label}>{el.value}</LabelizedField>
                </Grid>
              ))}
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
