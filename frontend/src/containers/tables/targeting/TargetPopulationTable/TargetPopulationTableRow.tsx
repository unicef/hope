import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { TargetPopulationNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { StatusBox } from '../../../../components/core/StatusBox';
import {
  targetPopulationStatusToColor,
  targetPopulationStatusMapping,
} from '../../../../utils/utils';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

interface TargetPopulationTableRowProps {
  targetPopulation: TargetPopulationNode;
  canViewDetails: boolean;
}

export function TargetPopulationTableRow({
  targetPopulation,
  canViewDetails,
}: TargetPopulationTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const targetPopulationDetailsPath = `/${businessArea}/target-population/${targetPopulation.id}`;
  const handleClick = (): void => {
    history.push(targetPopulationDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={targetPopulation.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={targetPopulationDetailsPath}>
            {targetPopulation.name}
          </BlackLink>
        ) : (
          targetPopulation.name
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={targetPopulation.status}
          statusToColor={targetPopulationStatusToColor}
          statusNameMapping={targetPopulationStatusMapping}
        />
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.program?.name || '-'}
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{targetPopulation.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{targetPopulation.updatedAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.createdBy?.firstName}{' '}
        {targetPopulation.createdBy?.lastName}
      </TableCell>
    </ClickableTableRow>
  );
}
