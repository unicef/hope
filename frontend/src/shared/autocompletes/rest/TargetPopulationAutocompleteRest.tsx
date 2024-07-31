import { fetchTargetPopulations } from '@api/targetPopulationApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { handleAutocompleteClose, handleOptionSelected } from '@utils/utils';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';

export const TargetPopulationAutocompleteRest = ({
  value,
  onChange,
}: {
  value;
  onChange: (e) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { businessArea, programId } = useBaseUrl();

  // Define the mapOptions function
  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.name,
      value: option.id,
    }));
  };

  return (
    <BaseAutocompleteRest
      value={value}
      label={t('Target Population')}
      dataCy="filters-target-population-autocomplete"
      fetchFunction={fetchTargetPopulations}
      businessArea={businessArea}
      programId={programId}
      handleChange={(_, selectedValue) => {
        if (!selectedValue) {
          onInputTextChange('');
        }
        onChange(selectedValue);
      }}
      handleOpen={() => setOpen(true)}
      open={open}
      handleClose={(_, reason) =>
        handleAutocompleteClose(setOpen, onInputTextChange, reason)
      }
      handleOptionSelected={(option, value1) =>
        handleOptionSelected(option?.value, value1)
      }
      handleOptionLabel={(option) => {
        return option === '' ? '' : option.name;
      }}
      inputValue={inputValue}
      onInputTextChange={onInputTextChange}
      debouncedInputText={debouncedInputText}
      startAdornment={null}
      mapOptions={mapOptions}
    />
  );
};
