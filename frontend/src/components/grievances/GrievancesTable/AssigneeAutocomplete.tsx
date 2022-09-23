import React, { useEffect, useState } from 'react';
import Autocomplete from '@material-ui/lab/Autocomplete';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import get from 'lodash/get';
import CircularProgress from '@material-ui/core/CircularProgress';
import { useDebounce } from '../../../hooks/useDebounce';
import TextField from '../../../shared/TextField';
import { renderUserName } from '../../../utils/utils';
import { useAllUsersForFiltersLazyQuery } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const AssigneeAutocomplete = ({
  disabled,
  fullWidth,
  onFilterChange,
  name,
  value,
  label,
}: {
  disabled?: boolean;
  fullWidth?: boolean;
  onFilterChange?;
  name?: string;
  value?;
  label?: string;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const businessArea = useBusinessArea();

  const [loadData, { data, loading }] = useAllUsersForFiltersLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'first_name,last_name,email',
      search: debouncedInputText,
    },
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  const onChangeMiddleware = (e, selectedValue): void => {
    onFilterChange((filters) => ({
      ...filters,
      [name]: selectedValue?.node?.id || undefined,
    }));
  };

  return (
    <StyledAutocomplete
      value={value}
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChangeMiddleware}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => {
        return value1?.node?.id === option.node.id;
      }}
      getOptionLabel={(option) => `${renderUserName(option.node)}`}
      disabled={disabled}
      options={get(data, 'allUsers.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label || t('Assignee')}
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? (
                  <CircularProgress color='inherit' size={20} />
                ) : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
};
