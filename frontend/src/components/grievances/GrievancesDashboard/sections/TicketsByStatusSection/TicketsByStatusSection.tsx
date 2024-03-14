import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';
import { TicketsByStatusChart } from '../../charts/TicketsByStatusChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByStatusSectionProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByStatus'];
}

export function TicketsByStatusSection({
  data,
}: TicketsByStatusSectionProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Status')}>
      <TicketsByStatusChart data={data} />
    </DashboardPaper>
  );
}
