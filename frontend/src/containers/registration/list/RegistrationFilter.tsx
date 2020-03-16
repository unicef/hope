import React from 'react';
import styled from 'styled-components';
import {
  TextField,
  InputAdornment,
  Select,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  createStyles,
  makeStyles,
} from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import GroupIcon from '@material-ui/icons/Group';
import PersonRoundedIcon from '@material-ui/icons/PersonRounded';
import { DatePicker } from '@material-ui/pickers';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import WcIcon from '@material-ui/icons/Wc';
import {
  useAllUsersQuery,
  useRegistrationChoicesQuery,
} from '../../../__generated__/graphql';
import { decodeIdString } from '../../../utils/utils';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;
const StyledDatePicker = styled(DatePicker)`
  .MuiFilledInput-root {
    border-radius: 4px;
  }
  && {
    width: 232px;
    color: #5f6368;
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:hover {
    border-bottom: 0;
    border-radius: 4px;
  }
  .MuiFilledInput-underline:hover::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after:hover {
    border-bottom: 0;
  }
  .MuiSvgIcon-root {
    color: #5f6368;
  }
  .MuiFilledInput-input {
    padding: 10px 15px 10px;
    cursor: pointer;
  }
  .MuiInputAdornment-filled.MuiInputAdornment-positionStart:not(.MuiInputAdornment-hiddenLabel) {
    margin: 0px;
  }
`;
const SelectAdormentWrapper = styled.div`
  background-color: rgba(0, 0, 0, 0.09);
  padding-left: 10px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  &:focus {
    background-color: rgba(0, 0, 0, 0.13);
  }
  &:hover {
    background-color: rgba(0, 0, 0, 0.13);
  }
`;
const IconWrapper = styled.div`
  color: #5f6368;
  align-items: center;
  display: flex;
`;
const SelectStyled = styled(Select)`
  && {
    width: ${({ theme }) => theme.spacing(58)}px;
    color: #5f6368;
    border-bottom-width: 0;
    border-radius: 4px;
    background-color: transparent;
  }
  .MuiFilledInput-input {
    padding: 10px 15px 10px;
    background-color: transparent;
  }
  .MuiSelect-select:focus {
    background-color: transparent;
  }
  &&.Mui-focused {
    background-color: transparent;
  }
  .MuiSelect-icon {
    color: #5f6368;
  }
  &&:hover {
    border-bottom-width: 0;
    border-radius: 4px;
    background-color: transparent;
  }
  &&:focus {
    background-color: transparent;
  }
  &&:hover::before {
    border-bottom-width: 0;
  }
  &&::before {
    border-bottom-width: 0;
  }
  &&::after {
    border-bottom-width: 0;
  }
  &&::after:hover {
    border-bottom-width: 0;
  }
`;

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;



interface RegistrationFiltersProps {
  onFilterChange;
  filter;
}
export function RegistrationFilters({
  onFilterChange,
  filter,
}: RegistrationFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name) =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const importedByLabel = React.useRef<HTMLLabelElement>(null);
  const [importedByLabelWidth, setImportedByLabelWidth] = React.useState(0);
  const statusLabel = React.useRef<HTMLLabelElement>(null);
  const [statusLabelWidth, setStatusLabelWidth] = React.useState(0);
  const { data: allUsersData } = useAllUsersQuery();
  const { data: registrationChoicesData } = useRegistrationChoicesQuery();
  React.useEffect(() => {
    if (!importedByLabel.current) {
      return;
    }
    setImportedByLabelWidth(importedByLabel.current.offsetWidth);
    setStatusLabelWidth(statusLabel.current.offsetWidth);
  }, [importedByLabel, statusLabel, allUsersData]);
  if (!allUsersData || !registrationChoicesData) {
    return null;
  }
  return (
    <Container>
      <TextField
        variant='outlined'
        margin='dense'
        onChange={(e) => handleFilterChange(e, 'search')}
        value={filter.search}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <StyledDatePicker
        variant='inline'
        inputVariant='outlined'
        margin='dense'
        label='Import'
        autoOk
        onChange={(date) => onFilterChange({ ...filter, importDate: date })}
        value={filter.importDate || null}
        format='DD/MM/YYYY'
        InputProps={{
          endAdornment: (
            <InputAdornment position='start'>
              <CalendarTodayRoundedIcon color='disabled' />
            </InputAdornment>
          ),
        }}
      />
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel ref={importedByLabel}>Imported By</InputLabel>
        <Select
          value={filter.importedBy || ''}
          labelWidth={importedByLabelWidth}
          onChange={(e) => handleFilterChange(e, 'importedBy')}
        >
          <MenuItem value=''>
            <em>None</em>
          </MenuItem>
          {allUsersData.allUsers.edges.map((edge) => {
            return (
              <MenuItem key={edge.node.id} value={decodeIdString(edge.node.id)}>
                {edge.node.firstName} {edge.node.lastName}
              </MenuItem>
            );
          })}
        </Select>
      </StyledFormControl>
      <StyledFormControl variant='outlined' margin='dense'>
        <InputLabel ref={statusLabel}>Status</InputLabel>
        <Select
          value={filter.status || ''}
          labelWidth={statusLabelWidth}
          onChange={(e) => handleFilterChange(e, 'status')}
        >
          <MenuItem value=''>
            <em>None</em>
          </MenuItem>
          {registrationChoicesData.registrationDataStatusChoices.map((item) => {
            return (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            );
          })}
        </Select>
      </StyledFormControl>
    </Container>
  );
}
