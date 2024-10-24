import * as React from 'react';
import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { Radio } from '@mui/material';
import { TargetPopulationNode } from '@generated/graphql';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import {
  targetPopulationStatusToColor,
  targetPopulationStatusMapping,
} from '@utils/utils';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface LookUpTargetPopulationTableRowSurveysProps {
  targetPopulation: TargetPopulationNode;
  canViewDetails: boolean;
  selectedTargetPopulation?;
  radioChangeHandler?: (id: string) => void;
}

export function LookUpTargetPopulationTableRowSurveys({
  targetPopulation,
  canViewDetails,
  radioChangeHandler,
  selectedTargetPopulation,
}: LookUpTargetPopulationTableRowSurveysProps): React.ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const targetPopulationDetailsPath = `/${baseUrl}/target-population/${targetPopulation.id}`;
  const handleClick = (): void => {
    if (radioChangeHandler !== undefined) {
      radioChangeHandler(targetPopulation.id);
    } else {
      navigate(targetPopulationDetailsPath);
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={targetPopulation.id}
    >
      {radioChangeHandler && (
        <TableCell padding="checkbox">
          <Radio
            color="primary"
            checked={selectedTargetPopulation === targetPopulation.id}
            onChange={() => {
              radioChangeHandler(targetPopulation.id);
            }}
            value={targetPopulation.id}
            name="radio-button-household"
            inputProps={{ 'aria-label': targetPopulation.id }}
          />
        </TableCell>
      )}
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={targetPopulationDetailsPath}>
            {targetPopulation.name}
          </BlackLink>
        ) : (
          targetPopulation.name
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={targetPopulation.status}
          statusToColor={targetPopulationStatusToColor}
          statusNameMapping={targetPopulationStatusMapping}
        />
      </TableCell>
      <TableCell align="left">
        {targetPopulation.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{targetPopulation.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{targetPopulation.updatedAt}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        {targetPopulation.createdBy?.firstName}{' '}
        {targetPopulation.createdBy?.lastName}
      </TableCell>
    </ClickableTableRow>
  );
}
