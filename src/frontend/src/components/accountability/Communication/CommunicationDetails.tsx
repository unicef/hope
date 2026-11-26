import { Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import type { ReactElement } from 'react';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { MessageDetail } from '@restgenerated/models/MessageDetail';

interface CommunicationDetailsProps {
  message: MessageDetail;
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
        <ResponsiveGridContainer spacing={6}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Created By')} value={message.createdBy} />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Date Created')}>
              <UniversalMoment>{message.createdAt}</UniversalMoment>
            </LabelizedField>
          </ResponsiveGrid>
          {message.paymentPlan ? (
            <ResponsiveGrid size="third" mobileSize="half">
              <LabelizedField label={t('Target Population')}>
                <BlackLink
                  to={`/${baseUrl}/target-population/${message?.paymentPlan.id}`}
                >
                  {message?.paymentPlan.name}
                </BlackLink>
              </LabelizedField>
            </ResponsiveGrid>
          ) : (
            <ResponsiveGrid size="third" mobileSize="half">
              <LabelizedField label={t('Target Population')}>-</LabelizedField>
            </ResponsiveGrid>
          )}
          {message.registrationDataImport && (
            <ResponsiveGrid size="third" mobileSize="half">
              <LabelizedField label={t('Registration Data Import')}>
                <BlackLink
                  to={`/${baseUrl}/registration-data-import/${message.registrationDataImport.id}`}
                >
                  {message.registrationDataImport.name}
                </BlackLink>
              </LabelizedField>
            </ResponsiveGrid>
          )}
        </ResponsiveGridContainer>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

export default withErrorBoundary(CommunicationDetails, 'CommunicationDetails');
