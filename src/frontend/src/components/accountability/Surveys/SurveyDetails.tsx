import { Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { choicesToDict, renderUserName } from '@utils/utils';
import { SurveyQuery, SurveysChoiceDataQuery } from '@generated/graphql';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface SurveyDetailsProps {
  survey: SurveyQuery['survey'];
  choicesData: SurveysChoiceDataQuery;
}

export function SurveyDetails({
  survey,
  choicesData,
}: SurveyDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const {
    category,
    title,
    createdBy,
    createdAt,
    targetPopulation,
    program,
    body,
  } = survey;
  const categoryDict = choicesToDict(choicesData.surveyCategoryChoices);

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Category')}
              value={categoryDict[category]}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Survey Title')} value={title} />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Created By')}
              value={renderUserName(createdBy)}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Date Created')}>
              <UniversalMoment>{createdAt}</UniversalMoment>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Target Population')}>
              {targetPopulation ? (
                <BlackLink
                  to={`/${baseUrl}/target-population/${targetPopulation.id}`}
                >
                  {targetPopulation.name}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Programme')}>
              {program ? (
                <BlackLink to={`/${baseUrl}/programmes/${program.id}`}>
                  {program.name}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField>
          </Grid>
          {body && (
            <Grid item xs={8}>
              <LabelizedField label={t('Message')} value={body} />
            </Grid>
          )}
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}
