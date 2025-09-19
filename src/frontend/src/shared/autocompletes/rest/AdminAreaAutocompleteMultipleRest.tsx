import { ReactElement, useEffect, useState } from 'react';
import { Checkbox } from '@mui/material';
import { useDebounce } from '@hooks/useDebounce';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  StyledAutocomplete,
  StyledTextField,
} from '@shared/autocompletes/StyledAutocomplete';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import { fetchAreas } from '@api/sharedApi';
import { capitalize } from 'lodash';

export function AdminAreaAutocompleteMultipleRest({
  value,
  onChange,
  level = 2,
  parentId = '',
  disabled = false,
  dataCy,
}: {
  value: string[];
  onChange: (e, option) => void;
  level?: number;
  disabled?: boolean;
  parentId?: string;
  dataCy: string;
}): ReactElement {
  const [inputValue, setInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 400);
  const [newValue, setNewValue] = useState([]);
  const { businessArea } = useBaseUrl();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (!businessArea || !level) {
        return;
      }

      setLoading(true);
      try {
        const queryParams: { [key: string]: string } = {
          limit: '100',
          name: capitalize(debouncedInputText),
          level: level.toString(),
        };

        if (parentId) {
          queryParams.parentId = parentId;
        }

        const queryString = new URLSearchParams(queryParams).toString();

        const fetchedData = await fetchAreas(businessArea, queryString);
        setData(fetchedData.results);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [debouncedInputText, businessArea, level, parentId]);

  useEffect(() => {
    if (data && value) {
      setNewValue(value);
    }
  }, [data, value]);

  useEffect(() => {
    if (value) {
      setInputTextChange('');
    }
  }, [value]);

  const options = (data || []).map((area) => ({
    name: area.name,
    value: area.id,
  }));

  // eslint-disable-next-line @typescript-eslint/no-shadow
  const handleChange = (event, newValue) => {
    setNewValue(newValue);
    onChange(event, newValue);
  };

  return (
    <StyledAutocomplete
      data-cy={dataCy}
      multiple
      disableCloseOnSelect
      fullWidth
      filterOptions={(options1) => options1}
      onChange={handleChange}
      value={newValue}
      getOptionLabel={(option: any) => option.name}
      disabled={disabled}
      options={options}
      loading={loading}
      isOptionEqualToValue={(option: any, value1: any) =>
        option.value === value1.value
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
          inputProps={{
            ...params.inputProps,
            value: inputValue,
          }}
          size="small"
          label={`Admin Level ${level}`}
          variant="outlined"
          value={inputValue}
          onChange={(e) => setInputTextChange(e.target.value)}
        />
      )}
    />
  );
}
