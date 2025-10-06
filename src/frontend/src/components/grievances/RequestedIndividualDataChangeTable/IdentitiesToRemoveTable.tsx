import {
  Box,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { TableTitle } from '@core/TableTitle';
import { handleSelected } from '../utils/helpers';
import { ReactElement } from 'react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

const GreenIcon = styled.div`
  color: #28cb15;
`;
const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface IdentitiesToRemoveTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketDetail;
  setFieldValue;
  countriesDict;
  identitiesToRemove;
  previousIdentities;
}

export function IdentitiesToRemoveTable({
  values,
  isEdit,
  ticket,
  countriesDict,
  identitiesToRemove,
  previousIdentities,
  setFieldValue,
}: IdentitiesToRemoveTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedIdentitiesToRemove } = values;
  const identitiesTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align="left" />
        <TableCell data-cy="table-cell-partner" align="left">
          {t('Partner')}
        </TableCell>
        <TableCell data-cy="table-cell-country" align="left">
          {t('Country')}
        </TableCell>
        <TableCell data-cy="table-cell-number" align="left">
          {t('Number')}
        </TableCell>
      </TableRow>
    </TableHead>
  );
  const handleSelectIdentityToRemove = (identityIndex): void => {
    handleSelected(
      identityIndex,
      'selectedIdentitiesToRemove',
      selectedIdentitiesToRemove,
      setFieldValue,
    );
  };

  return (
    <>
      <TableTitle>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">{t('Identities to be removed')}</Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        {identitiesTableHead}
        <TableBody>
          {identitiesToRemove?.map((row, index) => {
            const identity = previousIdentities[row.value];
            return (
              <TableRow key={`${identity.number}-${identity.country}`}>
                <TableCell align="left">
                  {isEdit ? (
                    <Checkbox
                      data-cy="checkbox-identity-to-remove"
                      onChange={(): void => {
                        handleSelectIdentityToRemove(index);
                      }}
                      color="primary"
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedIdentitiesToRemove.includes(index)}
                      inputProps={{ 'aria-labelledby': 'xd' }}
                    />
                  ) : (
                    selectedIdentitiesToRemove.includes(index) && (
                      <GreenIcon data-cy="green-check">
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align="left">{identity?.partner || '-'}</TableCell>
                <TableCell align="left">
                  {countriesDict[identity?.country] || '-'}
                </TableCell>
                <TableCell align="left">{identity?.number || '-'}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
}
