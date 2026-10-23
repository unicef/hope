import withErrorBoundary from '@components/core/withErrorBoundary';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Grid, Typography } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import type { ResponsiveGridSize } from 'src/responsive';
import type { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';
import type { ReactElement } from 'react';
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
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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
                label: t('Category'),
                value: <span>{t('Feedback')}</span>,
                size: 'quarter',
              },
              {
                label: t('Issue Type'),
                value: (
                  <span>
                    {feedback.issueType === 'POSITIVE_FEEDBACK'
                      ? 'Positive Feedback'
                      : 'Negative Feedback'}
                  </span>
                ),
                size: 'quarter',
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
                size: 'quarter',
              },
              {
                label:
                  isAllPrograms || isSocialDctType
                    ? t('Target ID')
                    : `${beneficiaryGroup?.memberLabel} ID`,
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
                size: 'quarter',
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
                size: 'quarter',
              },
              {
                label: t('Created By'),
                value: feedback.createdBy,
                size: 'quarter',
              },
              {
                label: t('Date Created'),
                value: <UniversalMoment>{feedback.createdAt}</UniversalMoment>,
                size: 'quarter',
              },
              {
                label: t('Last Modified Date'),
                value: <UniversalMoment>{feedback.updatedAt}</UniversalMoment>,
                size: 'quarter',
              },
              {
                label: t('Administrative Level 2'),
                value: feedback.admin2?.name,
                size: 'quarter',
              },
              {
                label: t('Area / Village / Pay point'),
                value: feedback.area,
                size: 'quarter',
              },
              {
                label: t('Languages Spoken'),
                value: feedback.language,
                size: 'quarter',
              },
              {
                label: t('Description'),
                value: feedback.description,
                size: 'full',
              },
              {
                label: t('Comments'),
                value: feedback.comments,
                size: 'full',
              },
            ]
              .filter((el) =>
                isSocialDctType
                  ? el.label !== `${beneficiaryGroup?.groupLabel} ID`
                  : el,
              )
              .map((el) => (
                <ResponsiveGrid
                  key={el.label}
                  size={el.size as ResponsiveGridSize}
                  mobileSize={el.size === 'quarter' ? 'half' : 'full'}
                >
                  <LabelizedField label={el.label}>{el.value}</LabelizedField>
                </ResponsiveGrid>
              ))}
          </ResponsiveGridContainer>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
}

export default withErrorBoundary(FeedbackDetails, 'FeedbackDetails');
