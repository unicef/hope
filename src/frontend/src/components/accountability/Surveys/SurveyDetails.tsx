import withErrorBoundary from '@components/core/withErrorBoundary';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Grid2 as Grid, Typography } from '@mui/material';
import { PaginatedSurveyCategoryChoiceList } from '@restgenerated/models/PaginatedSurveyCategoryChoiceList';
import { Survey } from '@restgenerated/models/Survey';
import { choicesToDict } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';

interface SurveyDetailsProps {
  survey: Survey;
  choicesData: PaginatedSurveyCategoryChoiceList;
}

function SurveyDetails({
  survey,
  choicesData,
}: SurveyDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, programId } = useBaseUrl();
  const {
    selectedProgram: { name: programName },
  } = useProgramContext();
  const { category, title, createdBy, createdAt, body } = survey;
  const categoryDict = choicesToDict(choicesData.results);

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Category')}
              value={categoryDict[category]}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Survey Title')} value={title} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Created By')} value={createdBy} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Date Created')}>
              <UniversalMoment>{createdAt}</UniversalMoment>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Target Population')}>
              {/* //TODO: is it correct id for the link below? */}
              {survey?.paymentPlan ? (
                <BlackLink
                  to={`/${baseUrl}/target-population/${survey?.paymentPlan}`}
                >
                  {survey?.paymentPlan}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Programme')}>
              <BlackLink to={`/${baseUrl}/programmes/${programId}`}>
                {programName}
              </BlackLink>
            </LabelizedField>
          </Grid>
          {body && (
            <Grid size={{ xs: 8 }}>
              <LabelizedField label={t('Message')} value={body} />
            </Grid>
          )}
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

export default withErrorBoundary(SurveyDetails, 'SurveyDetails');
