import { ReactElement } from 'react';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface PaymentPlanGroupTableRowProps {
  group: {
    id: string;
    unicefId: string;
    name: string;
    cycle: string;
  };
}

export const PaymentPlanGroupTableRow = ({
  group,
}: PaymentPlanGroupTableRowProps): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const groupPath = `/${baseUrl}/payment-module/groups/${group.id}`;

  return (
    <ClickableTableRow key={group.id}>
      <TableCell align="left">
        <BlackLink to={groupPath}>{group.name}</BlackLink>
      </TableCell>
      <TableCell align="left">{group.unicefId || '-'}</TableCell>
      <TableCell align="left">{group.cycle || '-'}</TableCell>
      <TableCell align="left">
        {/* TODO: PaymentPlanGroup has no status field yet — placeholder until API is ready */}
        -
      </TableCell>
    </ClickableTableRow>
  );
};
