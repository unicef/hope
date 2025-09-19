import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';
import {
  paymentPlanStatusMapping,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface LookUpTargetPopulationTableRowSurveysProps {
  targetPopulation: TargetPopulationList;
  canViewDetails: boolean;
  selectedTargetPopulation?;
  radioChangeHandler?: (id: string) => void;
}

export function LookUpTargetPopulationTableRowSurveys({
  targetPopulation,
  canViewDetails,
  radioChangeHandler,
  selectedTargetPopulation,
}: LookUpTargetPopulationTableRowSurveysProps): ReactElement {
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
            slotProps={{ input: { 'aria-label': targetPopulation.id } }}
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
          statusToColor={paymentPlanStatusToColor}
          statusNameMapping={paymentPlanStatusMapping}
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
      <TableCell align="left">{targetPopulation.createdBy}</TableCell>
    </ClickableTableRow>
  );
}
