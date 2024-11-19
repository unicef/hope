import { useTranslation } from 'react-i18next';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';
import { TicketsByCategoryChart } from '../../charts/TicketsByCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';
import { ReactElement } from 'react';

interface TicketsByCategorySectionProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByCategory'];
}

export function TicketsByCategorySection({
  data,
}: TicketsByCategorySectionProps): ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Category')}>
      <TicketsByCategoryChart data={data} />
    </DashboardPaper>
  );
}
