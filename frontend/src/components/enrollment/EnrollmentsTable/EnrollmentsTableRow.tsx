import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

import { enrollmentStatusToColor, renderUserName } from '../../../utils/utils';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { Missing } from '../../core/Missing';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';

interface EnrollmentsTableRowProps {
  targetPopulation: TargetPopulationNode;
  canViewDetails: boolean;
}

export const EnrollmentsTableRow = ({
  targetPopulation,
  canViewDetails,
}: EnrollmentsTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const enrollmentDetailsPath = `/${businessArea}/enrollment/${targetPopulation.id}`;
  const handleClick = (): void => {
    history.push(enrollmentDetailsPath);
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
          <BlackLink to={enrollmentDetailsPath}>
            {targetPopulation.name}
          </BlackLink>
        ) : (
          targetPopulation.name
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={targetPopulation.status}
          statusToColor={enrollmentStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{targetPopulation.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{targetPopulation.updatedAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        {renderUserName(targetPopulation.createdBy)}
      </TableCell>
    </ClickableTableRow>
  );
};
