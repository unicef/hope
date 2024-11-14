import { useTranslation } from 'react-i18next';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';
import { TicketsByLocationAndCategoryChart } from '../../charts/TicketsByLocationAndCategoryChart';
import { DashboardPaper } from '../../DashboardPaper';
import { ReactElement } from 'react';

interface TicketsByLocationAndCategorySectionProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByLocationAndCategory'];
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
