import { useTranslation } from 'react-i18next';
import { TicketsByLocationAndCategoryChart } from '../../charts/TicketsByLocationAndCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';
import { DetailedChartData } from '@restgenerated/models/DetailedChartData';
import { ReactElement } from 'react';

interface TicketsByLocationAndCategorySectionProps {
  data: DetailedChartData;
}

export function TicketsByLocationAndCategorySection({
  data,
}: TicketsByLocationAndCategorySectionProps): ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Category and Location')}>
      <TicketsByLocationAndCategoryChart data={data} />
    </DashboardPaper>
  );
}
