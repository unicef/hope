import { fetchRegistrationDataImports } from '@api/rdiApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { handleAutocompleteClose, handleOptionSelected } from '@utils/utils';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BaseAutocompleteRest } from './BaseAutocompleteRest';

export const RdiAutocompleteRest = ({
  disabled,
  value,
  onChange,
}: {
  disabled?;
  value?: string;
  onChange: (e) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const { businessArea, programId } = useBaseUrl();

  const mapOptions = (options) => {
    return options.map((option) => ({
      name: option.name,
      value: option.id,
    }));
  };

  return (
    <BaseAutocompleteRest
      value={value}
      disabled={disabled}
      label={t('Registration Data Import')}
      dataCy="filters-registration-data-import"
      // eslint-disable-next-line @typescript-eslint/no-shadow
      fetchFunction={(businessArea, programId, queryParams) =>
        fetchRegistrationDataImports(businessArea, programId, {
          status: 'MERGED',
          name: debouncedInputText,
          ...queryParams,
        })
      }
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
