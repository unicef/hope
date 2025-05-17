import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import {
  GrievanceTicketQuery,
  GrievancesChoiceDataQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Grid2 as Grid, GridSize, Typography } from '@mui/material';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import {
  choicesToDict,
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  renderUserName,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { replaceLabels } from '../utils/createGrievanceUtils';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface GrievancesDetailsProps {
  ticket: GrievanceTicketDetail;
  choicesData: GrievancesChoiceDataQuery;
  baseUrl: string;
  canViewHouseholdDetails: boolean;
  canViewIndividualDetails: boolean;
}

function GrievancesDetails({
  ticket,
  choicesData,
  baseUrl,
  canViewHouseholdDetails,
  canViewIndividualDetails,
}: GrievancesDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { isAllPrograms } = useBaseUrl();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
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
      GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT.toString() ||
    ticket.category.toString() ===
      GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION.toString();
  const showPartner =
    ticket.issueType === +GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT;

  const mappedDocumentation = (): ReactElement => (
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

  const renderPaymentUrl = (): ReactElement => {
    const paymentRecord = ticket?.paymentRecord;
    if (paymentRecord) {
      return (
        <ContentLink
          href={`/${baseUrl}/payment-module/payments/${paymentRecord.id}`}
        >
          {paymentRecord.unicefId}
        </ContentLink>
      );
    }
    return <>-</>;
  };

  const renderPaymentPlanUrl = (): ReactElement => {
    const parent = ticket?.paymentRecord?.parent;
    if (parent) {
      return (
        <ContentLink
          href={`/${baseUrl}/payment-module/payment-plans/${parent.id}`}
        >
          {parent.unicefId}
        </ContentLink>
      );
    }
    return <>-</>;
  };

  const renderPaymentPlanVerificationUrl = (): ReactElement => {
    const parent = ticket?.paymentRecord?.parent;
    if (parent) {
      const url = `/${baseUrl}/payment-verification/payment-plan/${parent.id}`;
      return <ContentLink href={url}>{parent.unicefId}</ContentLink>;
    }
    return <>-</>;
  };

  const mappedPrograms = (): ReactElement => {
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
    <Grid size={{ xs: 12 }}>
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
                value: (
                  <span>{replaceLabels(issueType, beneficiaryGroup)}</span>
                ),
                size: 3,
              },
              !isAllPrograms && {
                label: `${beneficiaryGroup?.groupLabel} ID`,
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
                label:
                  isAllPrograms || isSocialDctType
                    ? t('Target ID')
                    : `${beneficiaryGroup?.memberLabel} ID`,

                value:
                  isAllPrograms || isSocialDctType ? (
                    <div>{ticket?.targetId || '-'}</div>
                  ) : (
                    <span>
                      {ticket.individual?.id && canViewIndividualDetails ? (
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
                label: t('Grievance Supporting Documents'),
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
              .filter((el) =>
                isSocialDctType ? el.label !== 'Household ID' : el,
              )
              .map(
                (el) =>
                  el.label &&
                  el.value &&
                  el.size && (
                    <Grid key={el.label} size={{ xs: el.size as GridSize }}>
                      <LabelizedField label={el.label}>
                        {el.value}
                      </LabelizedField>
                    </Grid>
                  ),
              )}
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
}

export default withErrorBoundary(GrievancesDetails, 'GrievancesDetails');
