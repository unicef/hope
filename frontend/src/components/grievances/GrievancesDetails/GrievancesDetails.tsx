import { Box, Grid, GridSize, Typography } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  GrievanceTicketQuery,
  GrievancesChoiceDataQuery,
} from '../../../__generated__/graphql';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import {
  choicesToDict,
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  renderUserName,
} from '../../../utils/utils';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { ContentLink } from '../../core/ContentLink';
import { LabelizedField } from '../../core/LabelizedField';
import { OverviewContainer } from '../../core/OverviewContainer';
import { PhotoModal } from '../../core/PhotoModal/PhotoModal';
import { StatusBox } from '../../core/StatusBox';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { BlackLink } from '../../core/BlackLink';

interface GrievancesDetailsProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  choicesData: GrievancesChoiceDataQuery;
  baseUrl: string;
  canViewHouseholdDetails: boolean;
  canViewIndividualDetails: boolean;
}

export const GrievancesDetails = ({
  ticket,
  choicesData,
  baseUrl,
  canViewHouseholdDetails,
  canViewIndividualDetails,
}: GrievancesDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { isAllPrograms } = useBaseUrl();
  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketStatusChoices);

  const priorityChoicesData = choicesData.grievanceTicketPriorityChoices;
  const urgencyChoicesData = choicesData.grievanceTicketUrgencyChoices;

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

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
  const showPartner =
    ticket.issueType === +GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT;

  const mappedDocumentation = (): React.ReactElement => {
    return (
      <Box display="flex" flexDirection="column">
        {ticket.documentation?.length
          ? ticket.documentation.map((doc) => {
              if (doc.contentType.includes('image')) {
                return (
                  <PhotoModal
                    key={doc.id}
                    src={doc.filePath}
                    variant="link"
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

  const renderUrl = (
    obj,
    objType: string,
    href: string,
    displayedId: string,
  ): React.ReactElement => {
    if (isAllPrograms) {
      return <>{displayedId}</>;
    }

    if (obj?.objType === objType) {
      return <ContentLink href={href}>{displayedId}</ContentLink>;
    }

    return <>-</>;
  };

  const getUrl = (objType: string, id: string): string => {
    switch (objType) {
      case 'PaymentRecord':
        return `/${baseUrl}/payment-records/${id}`;
      case 'Payment':
        return `/${baseUrl}/payment-module/payments/${id}`;
      case 'PaymentPlan':
        return `/${baseUrl}/payment-module/payment-plans/${id}`;
      case 'CashPlan':
        return `/${baseUrl}/cashplans/${id}`;
      default:
        return '';
    }
  };

  const renderPaymentUrl = (): React.ReactElement => {
    const paymentRecord = ticket?.paymentRecord;
    if (paymentRecord) {
      return renderUrl(
        paymentRecord,
        paymentRecord.objType,
        getUrl(paymentRecord.objType, paymentRecord.id),
        paymentRecord.caId,
      );
    }
    return <>-</>;
  };

  const renderPaymentPlanUrl = (): React.ReactElement => {
    const parent = ticket?.paymentRecord?.parent;
    if (parent) {
      return renderUrl(
        parent,
        parent.objType,
        getUrl(parent.objType, parent.id),
        parent.unicefId,
      );
    }
    return <>-</>;
  };

  const renderPaymentPlanVerificationUrl = (): React.ReactElement => {
    const parent = ticket?.paymentRecord?.parent;
    if (parent) {
      const url = `/${baseUrl}/payment-verification/${
        parent.objType === 'CashPlan' ? 'cash-plan' : 'payment-plan'
      }/${parent.id}`;
      return renderUrl(parent, parent.objType, url, parent.unicefId);
    }
    return <>-</>;
  };

  const mappedPrograms = (): React.ReactElement => {
    if (!ticket.programs?.length) {
      return <>-</>;
    }
    return (
      <Box display="flex" flexDirection="column">
        {ticket.programs.map((program) => (
          <ContentLink
            key={program.id}
            href={`/${baseUrl}/details/${program.id}`}
          >
            {program.name}
          </ContentLink>
        ))}
      </Box>
    );
  };

  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
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
                      priorityChoicesData[
                        priorityChoicesData.findIndex(
                          (obj) => obj.value === ticket.priority,
                        )
                      ]?.name || '-'
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
                    status={
                      urgencyChoicesData[
                        urgencyChoicesData.findIndex(
                          (obj) => obj.value === ticket.urgency,
                        )
                      ]?.name || '-'
                    }
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
                    {ticket.household?.id &&
                    canViewHouseholdDetails &&
                    !isAllPrograms ? (
                      <BlackLink
                        to={`/${baseUrl}/population/household/${ticket.household.id}`}
                      >
                        {ticket.household.unicefId}
                      </BlackLink>
                    ) : (
                      <div>
                        {ticket.household?.id ? ticket.household.unicefId : '-'}
                      </div>
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Individual ID'),
                value: (
                  <span>
                    {ticket.individual?.id &&
                    canViewIndividualDetails &&
                    !isAllPrograms ? (
                      <BlackLink
                        to={`/${baseUrl}/population/individuals/${ticket.individual.id}`}
                      >
                        {ticket.individual.unicefId}
                      </BlackLink>
                    ) : (
                      <div>
                        {ticket.individual?.id
                          ? ticket.individual.unicefId
                          : '-'}
                      </div>
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Payment ID'),
                value: <span>{renderPaymentUrl()}</span>,
                size: 3,
              },
              {
                label: t('Payment Plan'),
                value: <span>{renderPaymentPlanUrl()}</span>,
                size: 3,
              },
              {
                label: t('Payment Plan Verification'),
                value: <span>{renderPaymentPlanVerificationUrl()}</span>,
                size: 3,
              },
              {
                label: t('Programme'),
                value: mappedPrograms(),
                size: 3,
              },
              showPartner && {
                label: t('Partner'),
                value: ticket.partner?.name,
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
