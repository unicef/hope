import { Box, Grid, GridSize, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import {
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  reduceChoices,
  renderUserName,
} from '../../../utils/utils';
import {
  GrievancesChoiceDataQuery,
  GrievanceTicketQuery,
} from '../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { ContentLink } from '../../core/ContentLink';
import { LabelizedField } from '../../core/LabelizedField';
import { OverviewContainer } from '../../core/OverviewContainer';
import { PhotoModal } from '../../core/PhotoModal/PhotoModal';
import { StatusBox } from '../../core/StatusBox';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

interface GrievancesDetailsProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  choicesData: GrievancesChoiceDataQuery;
  businessArea: string;
  canViewHouseholdDetails: boolean;
  canViewIndividualDetails: boolean;
}

export const GrievancesDetails = ({
  ticket,
  choicesData,
  businessArea,
  canViewHouseholdDetails,
  canViewIndividualDetails,
}: GrievancesDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const priorityChoicesData = choicesData.grievanceTicketPriorityChoices;
  const urgencyChoicesData = choicesData.grievanceTicketUrgencyChoices;

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const issueType = ticket.issueType
    ? choicesData.grievanceTicketIssueTypeChoices
        .filter((el) => el.category === ticket.category.toString())[0]
        .subCategories.filter(
          (el) => el.value === ticket.issueType.toString(),
        )[0].name
    : '-';

  const showIssueType =
    ticket.category.toString() ===
      GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE.toString() ||
    ticket.category.toString() ===
      GRIEVANCE_CATEGORIES.DATA_CHANGE.toString() ||
    ticket.category.toString() ===
      GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT.toString();
  const showProgramme =
    ticket.issueType !== +GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL;
  const showPartner =
    ticket.issueType === +GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT;

  const mappedDocumentation = (): React.ReactElement => {
    return (
      <Box display='flex' flexDirection='column'>
        {ticket.documentation?.length
          ? ticket.documentation.map((doc) => {
              if (doc.contentType.includes('image')) {
                return (
                  <PhotoModal
                    key={doc.id}
                    src={doc.filePath}
                    variant='link'
                    linkText={doc.name}
                  />
                );
              }
              return (
                <ContentLink key={doc.id} download href={doc.filePath}>
                  {doc.name}
                </ContentLink>
              );
            })
          : '-'}
      </Box>
    );
  };

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
                label: t('Status'),
                value: (
                  <StatusBox
                    status={statusChoices[ticket.status]}
                    statusToColor={grievanceTicketStatusToColor}
                  />
                ),
                size: 3,
              },
              {
                label: t('Priority'),
                value: (
                  <StatusBox
                    status={
                      priorityChoicesData[ticket.priority - 1]?.name || '-'
                    }
                    statusToColor={grievanceTicketBadgeColors}
                  />
                ),
                size: 3,
              },
              {
                label: t('Urgency'),
                value: (
                  <StatusBox
                    status={urgencyChoicesData[ticket.urgency - 1]?.name || '-'}
                    statusToColor={grievanceTicketBadgeColors}
                  />
                ),
                size: 3,
              },
              {
                label: t('Assigned to'),
                value: renderUserName(ticket.assignedTo),
                size: 3,
              },
              {
                label: t('Category'),
                value: <span>{categoryChoices[ticket.category]}</span>,
                size: 3,
              },
              showIssueType && {
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
                size: showIssueType ? 3 : 6,
              },
              {
                label: t('Payment ID'),
                value: (
                  <span>
                    {ticket.paymentRecord?.caId ? (
                      <ContentLink
                        href={`/${businessArea}/payment-records/${ticket.paymentRecord.id}`}
                      >
                        {ticket.paymentRecord.caId}
                      </ContentLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: showProgramme || showPartner ? 3 : 12,
              },
              showProgramme && {
                label: t('Programme'),
                value: ticket.programme?.name,
                size: showPartner ? 3 : 9,
              },
              showPartner && {
                label: t('Partner'),
                value: ticket.partner?.name,
                size: 6,
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
                size: 6,
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
                label: t('Documentation'),
                value: mappedDocumentation(),
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
