import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';
import { TicketsByLocationAndCategoryChart } from '../../charts/TicketsByLocationAndCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';

interface TicketsByLocationAndCategorySectionProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByLocationAndCategory'];
}

export function TicketsByLocationAndCategorySection({
  data,
}: TicketsByLocationAndCategorySectionProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardPaper noMarginTop title={t('Tickets by Category and Location')}>
      <TicketsByLocationAndCategoryChart data={data} />
    </DashboardPaper>
  );
}
