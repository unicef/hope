import { IconButton, Box } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import { Edit, Delete } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import { useConfirmation } from '../../../../components/core/ConfirmationDialog';
import { Missing } from '../../../../components/core/Missing';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  AllCashPlansQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';

interface FspTableRowProps {
  plan: AllCashPlansQuery['allCashPlans']['edges'][number]['node'];
  canViewDetails: boolean;
}

export const FspTableRow = ({
  plan,
  canViewDetails,
}: FspTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const confirm = useConfirmation();
  const { t } = useTranslation();
  const editFspPath = `/${businessArea}/payment-module/fsp/${plan.id}`;
  const dialogText = t('Are you sure you want to delete this FSP?');
  const handleClick = (): void => {
    history.push(editFspPath);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={plan.id}
    >
      <TableCell align='left'>{plan.id}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell>
        <Box display='flex' align-items='center'>
          <IconButton
            onClick={(e) => {
              e.stopPropagation();
              confirm({
                title: t('Warning'),
                content: dialogText,
              }).then(null);
            }}
          >
            <Delete />
          </IconButton>
          <IconButton
            onClick={() => {
              console.log('EDIT');
            }}
          >
            <Edit />
          </IconButton>
        </Box>
      </TableCell>
    </ClickableTableRow>
  );
};
