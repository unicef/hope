import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { renderUserName } from '../../../utils/utils';
import { SurveyQuery } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { Missing } from '../../core/Missing';
import { OverviewContainer } from '../../core/OverviewContainer';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

interface SurveyDetailsProps {
  survey: SurveyQuery['survey'];
}

export const SurveyDetails = ({
  survey,
}: SurveyDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const {
    category,
    title,
    createdBy,
    createdAt,
    targetPopulation,
    program,
    body,
  } = survey;

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={3}>
            <LabelizedField label={t('Category')} value={category} />
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
          <Grid item xs={4}>
            <Missing />
            <LabelizedField label={t('Target Population')}>
              {targetPopulation ? (
                <BlackLink
                  to={`/${businessArea}/target-population/${targetPopulation.id}`}
                >
                  {targetPopulation.name}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme')} value={program.name} />
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Message')}>
                <Box display='flex' flexDirection='column'>
                  {title}
                  {body}
                </Box>
              </LabelizedField>
            </Grid>
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
};
