import * as React from 'react';
import { useEffect, useState } from 'react';
import get from 'lodash/get';
import { Checkbox } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@hooks/useDebounce';
import { useAllAdminAreasQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  StyledAutocomplete,
  StyledTextField,
} from '@shared/autocompletes/StyledAutocomplete';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';

export function AdminAreaAutocompleteMultiple({
  value,
  onChange,
  level = 2,
  parentId = '',
  disabled = false,
}: {
  value: string[];
  onChange: (e, option) => void;
  level?: number;
  disabled?: boolean;
  parentId?: string;
}): React.ReactElement {
  const { t } = useTranslation();
  const [inputValue, setInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 400);
  const [newValue, setNewValue] = useState([]);
  const { businessArea } = useBaseUrl();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      name: debouncedInputText,
      businessArea,
      level,
      parentId,
    },
  });
  useEffect(() => {
    setNewValue(value);
  }, [data, value]);

  useEffect(() => {
    setInputTextChange('');
  }, [value]);

  const options = get(data, 'allAdminAreas.edges', []);
  return (
    <StyledAutocomplete
      multiple
      disableCloseOnSelect
      fullWidth
      filterOptions={(options1) => options1}
      onChange={onChange}
      value={newValue}
      getOptionLabel={(option: any) => {
        if (!option.node) {
          return '';
        }
        return `${option.node.name}`;
      }}
      disabled={disabled}
      options={options}
      loading={loading}
      isOptionEqualToValue={(option: any, value1: any) =>
        option.node.name === value1.node.name
      }
      renderOption={(props, option: any, { selected }) => (
        <li {...props}>
          <Checkbox
            icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
            checkedIcon={<CheckBoxIcon fontSize="small" />}
            style={{ marginRight: 8 }}
            checked={selected}
          />
          {option.node.name}
        </li>
      )}
      renderInput={(params) => (
        <StyledTextField
          {...params}
          inputProps={{
            ...params.inputProps,
            value: inputValue,
          }}
          size="small"
          placeholder={newValue.length > 0 ? null : t('Administrative Level 2')}
          variant="outlined"
          value={inputValue}
          onChange={(e) => setInputTextChange(e.target.value)}
        />
      )}
    />
  );
}
