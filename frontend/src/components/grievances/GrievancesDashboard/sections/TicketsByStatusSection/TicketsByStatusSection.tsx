import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllChartsQuery } from '../../../../../__generated__/graphql';
import { TicketsByStatusChart } from '../../charts/TicketsByStatusChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByStatusSectionProps {
  data: AllChartsQuery['chartIndividualsReachedByAgeAndGender'];
}

export const TicketsByStatusSection = ({
  data,
}: TicketsByStatusSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <DashboardPaper title={t('Tickets by Status')}>
      <TicketsByStatusChart data={data} />
    </DashboardPaper>
  );
};
