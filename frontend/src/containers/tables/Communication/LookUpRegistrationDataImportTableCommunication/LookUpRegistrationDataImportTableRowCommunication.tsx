import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import * as React from 'react';
import { Radio } from '@mui/material';
import { RegistrationDataImportNode } from '@generated/graphql';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import { registrationDataImportStatusToColor } from '@utils/utils';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';

interface LookUpRegistrationDataImportTableRowCommunicationProps {
  registrationDataImport: RegistrationDataImportNode;
  canViewDetails: boolean;
  selectedRDI?;
  radioChangeHandler?: (id: string) => void;
}

export function LookUpRegistrationDataImportTableRowCommunication({
  registrationDataImport,
  canViewDetails,
  selectedRDI,
  radioChangeHandler,
}: LookUpRegistrationDataImportTableRowCommunicationProps): React.ReactElement {
const navigate = useNavigate()  const businessArea = useBusinessArea();
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
      if (registrationDataImport.importedBy.firstName) {
        return `${registrationDataImport.importedBy.firstName} ${registrationDataImport.importedBy.lastName}`;
      }
      return registrationDataImport.importedBy.email;
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
        {registrationDataImport.totalHouseholdsCountWithValidPhoneNo || 0}
      </TableCell>
      <TableCell align="left">{renderImportedBy()}</TableCell>
      <TableCell align="left">{registrationDataImport.dataSource}</TableCell>
    </ClickableTableRow>
  );
}
