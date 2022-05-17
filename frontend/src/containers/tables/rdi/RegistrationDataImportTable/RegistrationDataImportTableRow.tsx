import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import React from 'react';
import { RegistrationDataImportNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { StatusBox } from '../../../../components/core/StatusBox';
import { registrationDataImportStatusToColor } from '../../../../utils/utils';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface PaymentRecordTableRowProps {
  registrationDataImport: RegistrationDataImportNode;
  canViewDetails: boolean;
}

export function RegistrationDataImportTableRow({
  registrationDataImport,
  canViewDetails,
}: PaymentRecordTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const importDetailsPath = `/${businessArea}/registration-data-import/${registrationDataImport.id}`;
  const handleClick = (): void => {
    history.push(importDetailsPath);
  };
  const renderImportedBy = (): string => {
    if (registrationDataImport?.importedBy) {
      if (registrationDataImport.importedBy.firstName) {
        return `${registrationDataImport.importedBy.firstName} ${registrationDataImport.importedBy.lastName}`;
      }
      return registrationDataImport.importedBy.email;
    }
    return "-";
  }
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={registrationDataImport.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={importDetailsPath}>
            {registrationDataImport.name}
          </BlackLink>
        ) : (
          registrationDataImport.name
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={registrationDataImport.status}
            statusToColor={registrationDataImportStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment withTime>
          {registrationDataImport.importDate}
        </UniversalMoment>
      </TableCell>
      <TableCell align='right'>
        {registrationDataImport.numberOfIndividuals}
      </TableCell>
      <TableCell align='right'>
        {registrationDataImport.numberOfHouseholds}
      </TableCell>
      <TableCell align='left'>{renderImportedBy()}</TableCell>
      <TableCell align='left'>{registrationDataImport.dataSource}</TableCell>
    </ClickableTableRow>
  );
}
