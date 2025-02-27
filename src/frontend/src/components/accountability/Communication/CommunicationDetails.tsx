import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { AccountabilityCommunicationMessageQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { renderUserName } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface CommunicationDetailsProps {
  message: AccountabilityCommunicationMessageQuery['accountabilityCommunicationMessage'];
}

function CommunicationDetails({
  message,
}: CommunicationDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  return (
    <ContainerColumnWithBorder data-cy="communication-details-container">
      <Title>
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Created By')}
              value={renderUserName(message.createdBy)}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Date Created')}>
              <UniversalMoment>{message.createdAt}</UniversalMoment>
            </LabelizedField>
          </Grid>
          {message.paymentPlan ? (
            <Grid size={{ xs: 4 }}>
              <LabelizedField label={t('Target Population')}>
                <BlackLink
                  to={`/${baseUrl}/target-population/${message?.paymentPlan.id}`}
                >
                  {message?.paymentPlan.name}
                </BlackLink>
              </LabelizedField>
            </Grid>
          ) : (
            <Grid size={{ xs: 4 }}>
              <LabelizedField label={t('Target Population')}>-</LabelizedField>
            </Grid>
          )}
          {message.registrationDataImport && (
            <Grid size={{ xs: 4 }}>
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
}

export default withErrorBoundary(CommunicationDetails, 'CommunicationDetails');
