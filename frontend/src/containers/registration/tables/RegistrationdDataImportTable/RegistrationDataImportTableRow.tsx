import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { RegistrationDataImportNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../../components/StatusBox';
import { registrationDataImportStatusToColor } from '../../../../utils/utils';
import { UniversalMoment } from '../../../../components/UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface PaymentRecordTableRowProps {
  registrationDataImport: RegistrationDataImportNode;
}

export function RegistrationDataImportTableRow({
  registrationDataImport,
}: PaymentRecordTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const name = registrationDataImport.importedBy.firstName
    ? `${registrationDataImport.importedBy.firstName} ${registrationDataImport.importedBy.lastName}`
    : registrationDataImport.importedBy.email;
  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/${registrationDataImport.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={registrationDataImport.id}
    >
      <TableCell align='left'>{registrationDataImport.name}</TableCell>
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
      <TableCell align='left'>{name}</TableCell>
      <TableCell align='left'>{registrationDataImport.dataSource}</TableCell>
    </ClickableTableRow>
  );
}
