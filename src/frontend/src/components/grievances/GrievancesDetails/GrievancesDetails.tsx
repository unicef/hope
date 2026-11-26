import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Grid, Typography } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import type { ResponsiveGridSize } from 'src/responsive';
import { GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import {
  choicesToDict,
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  renderUserName,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import {
  getIssueTypeToDisplay,
  isShowIssueType,
  replaceLabels,
} from '../utils/createGrievanceUtils';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';

interface GrievancesDetailsProps {
  ticket: GrievanceTicketDetail;
  choicesData: GrievanceChoices;
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
  const { isAllPrograms, businessArea } = useBaseUrl();
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

  const submissionChannelChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketSubmissionChannelChoices || []);

  const showIssueType = isShowIssueType(ticket.category);
  const issueTypeToDisplay = getIssueTypeToDisplay(
    ticket.issueType,
    choicesData.grievanceTicketIssueTypeChoices,
  );

  const showPartner =
    ticket.issueType === +GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT;

  const mappedDocumentation = (): ReactElement => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
      }}
    >
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
          href={`/${businessArea}/programs/${ticket.programs?.[0]?.code}/payment-module/payments/${paymentRecord.id}`}
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
          href={`/${businessArea}/programs/${ticket.programs?.[0]?.code}/payment-module/payment-plans/${parent.id}`}
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
      const url = `/${businessArea}/programs/${ticket.programs?.[0]?.code}/payment-verification/payment-plan/${parent.id}`;
      return <ContentLink href={url}>{parent.unicefId}</ContentLink>;
    }
    return <>-</>;
  };

  const mappedPrograms = (): ReactElement => {
    if (!ticket.programs?.length) {
      return <>-</>;
    }
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {ticket.programs.map((program) => (
          <ContentLink
            key={program.id}
            href={`/${baseUrl}/details/${program.code}`}
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
          <ResponsiveGridContainer spacing={6}>
            {[
              {
                label: t('Status'),
                value: (
                  <StatusBox
                    status={statusChoices[ticket.status ?? '']}
                    statusToColor={grievanceTicketStatusToColor}
                  />
                ),
                size: 'quarter',
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
                size: 'quarter',
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
                size: 'quarter',
              },
              {
                label: t('Assigned to'),
                value: renderUserName(ticket.assignedTo),
                size: 'quarter',
              },
              {
                label: t('Submission Channel'),
                value: (
                  <span>
                    {submissionChannelChoices[ticket.submissionChannel ?? ''] ||
                      '-'}
                  </span>
                ),
                size: 'quarter',
              },
              {
                label: t('Category'),
                value: <span>{categoryChoices[ticket.category]}</span>,
                size: 'quarter',
              },
              showIssueType && {
                label: t('Issue Type'),
                value: (
                  <span>
                    {replaceLabels(issueTypeToDisplay, beneficiaryGroup)}
                  </span>
                ),
                size: 'quarter',
              },
              !isSocialDctType && {
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
                size: 'quarter',
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
                size: 'quarter',
              },
              {
                label: t('Payment ID'),
                value: <span>{renderPaymentUrl()}</span>,
                size: 'quarter',
              },
              {
                label: t('Payment Plan'),
                value: <span>{renderPaymentPlanUrl()}</span>,
                size: 'quarter',
              },
              {
                label: t('Payment Plan Verification'),
                value: <span>{renderPaymentPlanVerificationUrl()}</span>,
                size: 'quarter',
              },
              {
                label: t('Programme'),
                value: mappedPrograms(),
                size: 'quarter',
              },
              showPartner && {
                label: t('Partner'),
                value: ticket.partner?.name,
                size: 'quarter',
              },
              {
                label: t('Created By'),
                value: renderUserName(ticket.createdBy),
                size: 'quarter',
              },
              {
                label: t('Date Created'),
                value: <UniversalMoment>{ticket.createdAt}</UniversalMoment>,
                size: 'quarter',
              },
              {
                label: t('Last Modified Date'),
                value: <UniversalMoment>{ticket.updatedAt}</UniversalMoment>,
                size: 'quarter',
              },
              {
                label: t('Administrative Level 2'),
                value: ticket.admin,
                size: 'quarter',
              },
              {
                label: t('Area / Village / Pay point'),
                value: ticket.area,
                size: 'quarter',
              },
              {
                label: t('Languages Spoken'),
                value: ticket.language,
                size: 'quarter',
              },
              {
                label: t('Grievance Supporting Documents'),
                value: mappedDocumentation(),
                size: 'quarter',
              },
              {
                label: t('Description'),
                value: ticket.description,
                size: 'full',
              },
              {
                label: t('Comments'),
                value: ticket.comments,
                size: 'full',
              },
            ]
              .filter((el) =>
                isSocialDctType
                  ? el.label !== `${beneficiaryGroup?.groupLabel} ID`
                  : el,
              )
              .map(
                (el) =>
                  el.label &&
                  el.value &&
                  el.size && (
                    <ResponsiveGrid
                      key={el.label}
                      size={el.size as ResponsiveGridSize}
                      mobileSize={el.size === 'quarter' ? 'half' : 'full'}
                    >
                      <LabelizedField label={el.label}>
                        {el.value}
                      </LabelizedField>
                    </ResponsiveGrid>
                  ),
              )}
          </ResponsiveGridContainer>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
}

export default withErrorBoundary(GrievancesDetails, 'GrievancesDetails');
