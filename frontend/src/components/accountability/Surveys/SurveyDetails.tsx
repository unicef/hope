import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { renderUserName } from '../../../utils/utils';
import { FeedbackQuery } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { Missing } from '../../core/Missing';
import { OverviewContainer } from '../../core/OverviewContainer';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

interface SurveyDetailsProps {
  message: FeedbackQuery['feedback'];
}

export const SurveyDetails = ({
  message,
}: SurveyDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  return (
    <ContainerColumnWithBorder data-cy='communication-details-container'>
      <Title>
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={3}>
            <LabelizedField label={t('Category')} value={<Missing />} />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Survey Title')} value={<Missing />} />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Created By')}
              value={renderUserName(message.createdBy)}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Date Created')}>
              <UniversalMoment>{message.createdAt}</UniversalMoment>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <Missing />
            {/* <LabelizedField label={t('Target Population')}>
              {message.targetPopulation ? (
                <BlackLink
                  to={`/${businessArea}/target-population/${message.targetPopulation.id}`}
                >
                  {message.targetPopulation.name}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField> */}
            <Grid item xs={3}>
              <LabelizedField label={t('Programme')} value={<Missing />} />
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Message')} value={<Missing />} />
            </Grid>
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
};
