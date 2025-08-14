import { useTranslation } from 'react-i18next';
import { TicketsByStatusChart } from '../../charts/TicketsByStatusChart';
import { DashboardPaper } from '../../DashboardPaper';
import { ChartData } from '@restgenerated/models/ChartData';
import { ReactElement } from 'react';

interface TicketsByStatusSectionProps {
  data: ChartData;
}

export function TicketsByStatusSection({
  data,
}: TicketsByStatusSectionProps): ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Status')}>
      <TicketsByStatusChart data={data} />
    </DashboardPaper>
  );
}
