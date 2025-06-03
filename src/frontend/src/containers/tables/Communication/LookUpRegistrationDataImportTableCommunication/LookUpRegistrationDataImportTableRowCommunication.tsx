import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { RegistrationDataImportList } from '@restgenerated/models/RegistrationDataImportList';
import { registrationDataImportStatusToColor } from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface LookUpRegistrationDataImportTableRowCommunicationProps {
  registrationDataImport: RegistrationDataImportList;
  canViewDetails: boolean;
  selectedRDI?;
  radioChangeHandler?: (id: string) => void;
}

export function LookUpRegistrationDataImportTableRowCommunication({
  registrationDataImport,
  canViewDetails,
  selectedRDI,
  radioChangeHandler,
}: LookUpRegistrationDataImportTableRowCommunicationProps): ReactElement {
  const navigate = useNavigate();
  const businessArea = useBusinessArea();
  const importDetailsPath = `/${businessArea}/registration-data-import/${registrationDataImport.id}`;
  const handleClick = (): void => {
    if (radioChangeHandler !== undefined) {
      radioChangeHandler(registrationDataImport.id);
    } else {
      navigate(importDetailsPath);
    }
  };
  const renderImportedBy = (): string => {
    if (registrationDataImport?.importedBy) {
      return registrationDataImport.importedBy || '-';
    }
    return '-';
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={registrationDataImport.id}
    >
      {radioChangeHandler && (
        <TableCell padding="checkbox">
          <Radio
            color="primary"
            checked={selectedRDI === registrationDataImport.id}
            onChange={() => {
              radioChangeHandler(registrationDataImport.id);
            }}
            value={registrationDataImport.id}
            name="radio-button-household"
            inputProps={{ 'aria-label': registrationDataImport.id }}
          />
        </TableCell>
      )}
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={importDetailsPath}>
            {registrationDataImport.name}
          </BlackLink>
        ) : (
          registrationDataImport.name
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={registrationDataImport.status}
          statusToColor={registrationDataImportStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        <UniversalMoment withTime>
          {registrationDataImport.importDate}
        </UniversalMoment>
      </TableCell>
      <TableCell align="right">
        {registrationDataImport.numberOfHouseholds || 0}
      </TableCell>
      <TableCell align="left">{renderImportedBy()}</TableCell>
      <TableCell align="left">{registrationDataImport.dataSource}</TableCell>
    </ClickableTableRow>
  );
}
