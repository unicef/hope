import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { Radio } from '@mui/material';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import {
  paymentPlanStatusToColor,
  targetPopulationStatusDisplayMap,
} from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface TargetPopulationTableRowProps {
  targetPopulation: PaymentPlanDetail;
  canViewDetails: boolean;
  selectedTargetPopulation?;
  radioChangeHandler?: (id: string) => void;
}

export function TargetPopulationForPeopleTableRow({
  targetPopulation,
  canViewDetails,
  radioChangeHandler,
  selectedTargetPopulation,
}: TargetPopulationTableRowProps): ReactElement {
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
          statusToColor={paymentPlanStatusToColor}
          statusNameMapping={targetPopulationStatusDisplayMap}
        />
      </TableCell>
      <TableCell align="left">
        {targetPopulation.total_households_count || '0'}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{targetPopulation.created_at}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{targetPopulation.updated_at}</UniversalMoment>
      </TableCell>
      <TableCell align="left">{targetPopulation.created_by}</TableCell>
    </ClickableTableRow>
  );
}
