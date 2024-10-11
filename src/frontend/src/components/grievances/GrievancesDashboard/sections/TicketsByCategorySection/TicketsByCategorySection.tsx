import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';
import { TicketsByCategoryChart } from '../../charts/TicketsByCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByCategorySectionProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByCategory'];
}

export function TicketsByCategorySection({
  data,
}: TicketsByCategorySectionProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Category')}>
      <TicketsByCategoryChart data={data} />
    </DashboardPaper>
  );
}
