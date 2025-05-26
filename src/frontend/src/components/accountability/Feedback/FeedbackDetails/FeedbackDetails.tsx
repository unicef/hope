import withErrorBoundary from '@components/core/withErrorBoundary';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { FeedbackIssueType } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Grid2 as Grid, GridSize, Typography } from '@mui/material';
import { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';
import { renderUserName } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';

interface FeedbackDetailsProps {
  feedback: FeedbackDetail;
  canViewHouseholdDetails: boolean;
  canViewIndividualDetails: boolean;
}

function FeedbackDetails({
  feedback,
  canViewHouseholdDetails,
  canViewIndividualDetails,
}: FeedbackDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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
                label: t('Category'),
                value: <span>{t('Feedback')}</span>,
                size: 3,
              },
              {
                label: t('Issue Type'),
                value: (
                  <span>
                    {feedback.issueType === FeedbackIssueType.PositiveFeedback
                      ? 'Positive Feedback'
                      : 'Negative Feedback'}
                  </span>
                ),
                size: 3,
              },
              {
                label: `${beneficiaryGroup?.groupLabel} ID`,
                value: (
                  <span>
                    {feedback.householdId &&
                    canViewHouseholdDetails &&
                    !isAllPrograms ? (
                      <BlackLink
                        to={`/${baseUrl}/population/household/${feedback.householdId}`}
                      >
                        {feedback.householdUnicefId}
                      </BlackLink>
                    ) : (
                      <div>
                        {feedback.householdId
                          ? feedback.householdUnicefId
                          : '-'}
                      </div>
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: `${beneficiaryGroup?.memberLabel} ID`,
                value: (
                  <span>
                    {feedback.individualId &&
                    canViewIndividualDetails &&
                    !isAllPrograms ? (
                      <BlackLink
                        to={`/${baseUrl}/population/individuals/${feedback.individualId}`}
                      >
                        {feedback.individualUnicefId}
                      </BlackLink>
                    ) : (
                      <div>
                        {feedback.individualId
                          ? feedback.individualUnicefId
                          : '-'}
                      </div>
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Programme'),
                value: (
                  <span>
                    {feedback.programId ? (
                      <BlackLink
                        to={`/${baseUrl}/details/${feedback.programId}`}
                      >
                        {feedback.programName}
                      </BlackLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Created By'),
                value: renderUserName(feedback.createdBy),
                size: 3,
              },
              {
                label: t('Date Created'),
                value: <UniversalMoment>{feedback.createdAt}</UniversalMoment>,
                size: 3,
              },
              {
                label: t('Last Modified Date'),
                value: <UniversalMoment>{feedback.updatedAt}</UniversalMoment>,
                size: 3,
              },
              {
                label: t('Administrative Level 2'),
                value: feedback.admin2?.name,
                size: 3,
              },
              {
                label: t('Area / Village / Pay point'),
                value: feedback.area,
                size: 3,
              },
              {
                label: t('Languages Spoken'),
                value: feedback.language,
                size: 3,
              },
              {
                label: t('Description'),
                value: feedback.description,
                size: 12,
              },
              {
                label: t('Comments'),
                value: feedback.comments,
                size: 12,
              },
            ]
              .filter((el) => el)
              .map((el) => (
                <Grid key={el.label} size={{ xs: el.size as GridSize }}>
                  <LabelizedField label={el.label}>{el.value}</LabelizedField>
                </Grid>
              ))}
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
}

export default withErrorBoundary(FeedbackDetails, 'FeedbackDetails');
