import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllGrievanceDashboardChartsQuery } from '../../../../../__generated__/graphql';
import { TicketsByCategoryChart } from '../../charts/TicketsByCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByCategorySectionProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByCategory'];
}

export const TicketsByCategorySection = ({
  data,
}: TicketsByCategorySectionProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Category')}>
      <TicketsByCategoryChart data={data} />
    </DashboardPaper>
  );
};
