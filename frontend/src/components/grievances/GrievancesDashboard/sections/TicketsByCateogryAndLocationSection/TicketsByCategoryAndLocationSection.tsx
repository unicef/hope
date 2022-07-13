import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllChartsQuery } from '../../../../../__generated__/graphql';
import { TicketsByCategoryAndLocationChart } from '../../charts/TicketsByCategoryAndLocationChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByCategoryAndLocationSectionProps {
  data?: AllChartsQuery['chartIndividualsReachedByAgeAndGender'];
}

export const TicketsByCategoryAndLocationSection = ({
  data,
}: TicketsByCategoryAndLocationSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <DashboardPaper title={t('Tickets by Category and Location')}>
      <TicketsByCategoryAndLocationChart />
    </DashboardPaper>
  );
};
