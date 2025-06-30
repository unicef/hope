import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { Radio } from '@mui/material';
import { RegistrationDataImportList } from '@restgenerated/models/RegistrationDataImportList';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import { registrationDataImportStatusToColor } from '@utils/utils';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

interface RegistrationDataImportForPeopleTableRowProps {
  registrationDataImport: RegistrationDataImportList;
  canViewDetails: boolean;
  selectedRDI?;
  radioChangeHandler?: (id: string) => void;
}

export function RegistrationDataImportForPeopleTableRow({
  registrationDataImport,
  canViewDetails,
  selectedRDI,
  radioChangeHandler,
}: RegistrationDataImportForPeopleTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const importDetailsForPeoplePath = `/${baseUrl}/registration-data-import/${registrationDataImport.id}`;
  const handleClick = (): void => {
    navigate(importDetailsForPeoplePath);
  };
  const renderImportedBy = (): string => {
    return registrationDataImport?.importedBy || '-';
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
          <BlackLink to={importDetailsForPeoplePath}>
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
      <TableCell align="center">
        {registrationDataImport.biometricDeduplicated}
      </TableCell>
      <TableCell align="right">
        {registrationDataImport.numberOfIndividuals}
      </TableCell>
      <TableCell align="left">{renderImportedBy()}</TableCell>
      <TableCell align="left">{registrationDataImport.dataSource}</TableCell>
    </ClickableTableRow>
  );
}
