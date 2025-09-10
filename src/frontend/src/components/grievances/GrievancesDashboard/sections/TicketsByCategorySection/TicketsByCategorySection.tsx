import { useTranslation } from 'react-i18next';
import { TicketsByCategoryChart } from '../../charts/TicketsByCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';
import { ChartData } from '@restgenerated/models/ChartData';
import { ReactElement } from 'react';

interface TicketsByCategorySectionProps {
  data: ChartData;
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
