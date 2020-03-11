import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import {
  ImportedHouseholdMinimalFragment,
  ImportedHouseholdNode, ImportedIndividualMinimalFragment,
  RegistrationDataImportNode,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../../components/StatusBox';
import {
  decodeIdString,
  registrationDataImportStatusToColor,
} from '../../../../utils/utils';
import moment from 'moment';

const StatusContainer = styled.div`
  width: 120px;
`;

interface ImportedIndividualsTableRowProps {
  individual: ImportedIndividualMinimalFragment;
}

export function ImportedIndividualsTableRow({
                                              individual,
}: ImportedIndividualsTableRowProps) {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/individual/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      key={individual.id}
    >
      <TableCell align='left'>{decodeIdString(individual.id)}</TableCell>
      <TableCell align='left'>
        {individual.fullName}
      </TableCell>
      <TableCell align='right'>{individual.workStatus}</TableCell>
      <TableCell align='left'>
        {moment(individual.dob).format('DD MMM YYYY')}
      </TableCell>
      <TableCell align='left'>{individual.sex}</TableCell>
    </ClickableTableRow>
  );
}
