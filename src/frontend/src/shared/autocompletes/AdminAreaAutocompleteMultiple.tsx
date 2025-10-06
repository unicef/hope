import { ReactElement, useEffect, useState } from 'react';
import { Checkbox } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useDebounce } from '@hooks/useDebounce';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
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
}): ReactElement {
  const { t } = useTranslation();
  const [inputValue, setInputTextChange] = useState('');

  const debouncedInputText = useDebounce(inputValue, 400);
  const [newValue, setNewValue] = useState([]);
  const { businessArea } = useBaseUrl();
  const { data: areasData, isLoading } = useQuery({
    queryKey: ['adminAreas', debouncedInputText, businessArea, level, parentId],
    queryFn: () =>
      RestService.restAreasList({
        search: debouncedInputText,
        areaTypeAreaLevel: level,
        parentId: parentId || undefined,
        limit: 100,
      }),
  });

  const loading = isLoading;
  useEffect(() => {
    setNewValue(value);
  }, [areasData, value]);

  useEffect(() => {
    setInputTextChange('');
  }, [value]);

  const options = areasData?.results || [];
  return (
    <StyledAutocomplete
      multiple
      disableCloseOnSelect
      fullWidth
      filterOptions={(options1) => options1}
      onChange={onChange}
      value={newValue}
      getOptionLabel={(option: any) => {
        if (!option) {
          return '';
        }
        return `${option.name}`;
      }}
      disabled={disabled}
      options={options}
      loading={loading}
      isOptionEqualToValue={(option: any, value1: any) =>
        option.name === value1.name
      }
      renderOption={(props, option: any, { selected }) => (
        <li {...props}>
          <Checkbox
            icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
            checkedIcon={<CheckBoxIcon fontSize="small" />}
            style={{ marginRight: 8 }}
            checked={selected}
          />
          {option.name}
        </li>
      )}
      renderInput={(params) => (
        <StyledTextField
          {...params}
          slotProps={{
            htmlInput: {
              ...params.inputProps,
              value: inputValue,
            },
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
