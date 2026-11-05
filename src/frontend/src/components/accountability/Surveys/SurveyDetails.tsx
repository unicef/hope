import withErrorBoundary from '@components/core/withErrorBoundary';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Typography } from '@mui/material';
import type { Survey } from '@restgenerated/models/Survey';
import type { ReactElement } from 'react';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';

interface SurveyDetailsProps {
  survey: Survey;
}

function SurveyDetails({ survey }: SurveyDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, programId } = useBaseUrl();
  const {
    selectedProgram: { name: programName },
  } = useProgramContext();
  const { category, title, createdBy, createdAt, body } = survey;

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <ResponsiveGridContainer spacing={6}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Category')} value={category} />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Survey Title')} value={title} />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Created By')} value={createdBy} />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Date Created')}>
              <UniversalMoment>{createdAt}</UniversalMoment>
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Target Population')}>
              {survey?.paymentPlan ? (
                <BlackLink
                  to={`/${baseUrl}/target-population/${survey?.paymentPlan}`}
                >
                  {survey?.paymentPlanName}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Programme')}>
              <BlackLink to={`/${baseUrl}/programmes/${programId}`}>
                {programName}
              </BlackLink>
            </LabelizedField>
          </ResponsiveGrid>
          {body && (
            <ResponsiveGrid size="twoThirds">
              <LabelizedField label={t('Message')} value={body} />
            </ResponsiveGrid>
          )}
        </ResponsiveGridContainer>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

export default withErrorBoundary(SurveyDetails, 'SurveyDetails');
