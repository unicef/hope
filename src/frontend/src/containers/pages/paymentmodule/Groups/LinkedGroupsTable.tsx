import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import type { PaymentPlanGroupLinked } from '@restgenerated/models/PaymentPlanGroupLinked';
import { paymentPlanStatusToColor } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { planTypeDisplayLabel } from './utils';

interface LinkedGroupsTableProps {
  linkedGroups: PaymentPlanGroupLinked[];
}

/** Follow-up, Top-Up and Amendment groups created from this group. */
export function LinkedGroupsTable({
  linkedGroups,
}: LinkedGroupsTableProps): ReactElement | null {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  if (!linkedGroups.length) return null;

  return (
    <ContainerColumnWithBorder data-cy="linked-groups">
      <Title>
        <Typography variant="h6">{t('Linked Payment Plans')}</Typography>
      </Title>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Name')}</TableCell>
            <TableCell>{t('Type')}</TableCell>
            <TableCell>{t('Status')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {linkedGroups.map((linked) => (
            <TableRow key={linked.id} data-cy="linked-group-row">
              <TableCell>
                <BlackLink
                  to={`/${baseUrl}/payment-module/groups/${linked.id}`}
                >
                  {linked.unicefId ?? linked.id}
                </BlackLink>
              </TableCell>
              <TableCell>{linked.name}</TableCell>
              <TableCell>{t(planTypeDisplayLabel(linked.planType))}</TableCell>
              <TableCell>
                {linked.status && (
                  <StatusBox
                    status={linked.status}
                    statusToColor={paymentPlanStatusToColor}
                  />
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </ContainerColumnWithBorder>
  );
}
