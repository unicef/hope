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
const GreyText = styled.div`
  color: #9e9e9e;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface IdentitiesToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketDetail;
  setFieldValue;
  countriesDict;
  index;
  identity;
}

export function IdentitiesToEditTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  countriesDict,
  index,
  identity,
}: IdentitiesToEditTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedIdentitiesToEdit } = values;
  const renderNewOrNotUpdated = (prev, curr): ReactElement => {
    if (prev === curr) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    return <span>{curr}</span>;
  };
  const handleSelectIdentityToEdit = (identityIndex): void => {
    handleSelected(
      identityIndex,
      'selectedIdentitiesToEdit',
      selectedIdentitiesToEdit,
      setFieldValue,
    );
  };

  const getPreviousPartner = (previousIdentity): string =>
    previousIdentity.partner || previousIdentity.agency;

  return (
    <>
      <TableTitle>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">{t('Identity to be edited')}</Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align="left">
              {isEdit ? (
                <Checkbox
                  color="primary"
                  onChange={(): void => {
                    handleSelectIdentityToEdit(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedIdentitiesToEdit.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedIdentitiesToEdit.includes(index) && (
                  <GreenIcon data-cy="green-check">
                    <CheckCircleIcon />
                  </GreenIcon>
                )
              )}
            </TableCell>
            <TableCell align="left">{t('Field')}</TableCell>
            <TableCell align="left">{t('Current Value')}</TableCell>
            <TableCell align="left">{t('New Value')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell />
            <TableCell align="left">{t('Partner')}</TableCell>
            <TableCell align="left">
              {getPreviousPartner(identity.previousValue)}
            </TableCell>
            <TableCell align="left">
              {identity.value?.partner ?? (
                <GreyText>{t('Not updated')}</GreyText>
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align="left">{t('Country')}</TableCell>
            <TableCell align="left">
              {countriesDict[identity.previousValue.country]}
            </TableCell>
            <TableCell align="left">
              {renderNewOrNotUpdated(
                countriesDict[identity.previousValue.country],
                countriesDict[identity.value?.country],
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align="left">{t('Identity Number')}</TableCell>
            <TableCell align="left">{identity.previousValue.number}</TableCell>
            <TableCell align="left">
              {renderNewOrNotUpdated(
                identity.previousValue.number,
                identity.value?.number,
              )}
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </>
  );
}
