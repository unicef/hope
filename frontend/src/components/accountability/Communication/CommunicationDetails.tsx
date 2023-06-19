import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AccountabilityCommunicationMessageQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { renderUserName } from '../../../utils/utils';
import { BlackLink } from '../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { OverviewContainer } from '../../core/OverviewContainer';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

interface CommunicationDetailsProps {
  message: AccountabilityCommunicationMessageQuery['accountabilityCommunicationMessage'];
}

export const CommunicationDetails = ({
  message,
}: CommunicationDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  return (
    <ContainerColumnWithBorder data-cy='communication-details-container'>
      <Title>
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
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
          {message.targetPopulation && (
            <Grid item xs={4}>
              <LabelizedField label={t('Target Population')}>
                <BlackLink
                  to={`/${baseUrl}/target-population/${message.targetPopulation.id}`}
                >
                  {message.targetPopulation.name}
                </BlackLink>
              </LabelizedField>
            </Grid>
          )}
          {message.registrationDataImport && (
            <Grid item xs={4}>
              <LabelizedField label={t('Registration Data Import')}>
                <BlackLink
                  to={`/${baseUrl}/registration-data-import/${message.registrationDataImport.id}`}
                >
                  {message.registrationDataImport.name}
                </BlackLink>
              </LabelizedField>
            </Grid>
          )}
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
};
