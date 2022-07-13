import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllChartsQuery } from '../../../../../__generated__/graphql';
import { TicketsByCategoryChart } from '../../charts/TicketsByCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByCategorySectionProps {
  data?: AllChartsQuery['chartIndividualsReachedByAgeAndGender'];
}

export const TicketsByCategorySection = ({
  data,
}: TicketsByCategorySectionProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <DashboardPaper title={t('Tickets by Category')}>
      <TicketsByCategoryChart />
    </DashboardPaper>
  );
};
