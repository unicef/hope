import { Grid2 as Grid, MenuItem } from '@mui/material';
import { SelectFilter } from '@core/SelectFilter';
import { SearchTextField } from '@core/SearchTextField';
import { ChoiceObject } from '@generated/graphql';
import { useTranslation } from 'react-i18next';

interface DocumentSearchFieldProps {
  onChange: (key: string, value: string) => void;
  type: string;
  number: string;
  choices: ChoiceObject[];
}

export const DocumentSearchField = ({
  onChange,
  type,
  number,
  choices = [],
}: DocumentSearchFieldProps) => {
  const { t } = useTranslation();

  return (
    <Grid container  size={{ xs: 6 }} spacing={0}>
      <Grid size={{ xs: 4 }}>
        <SelectFilter
          onChange={(e) => onChange('documentType', e.target.value)}
          label={t('Document Type')}
          value={type}
          borderRadius="0px 4px 4px 0px"
          data-cy="filters-document-type"
          fullWidth
          disableClearable
        >
          {choices.map(({ name, value }) => (
            <MenuItem key={value} value={value}>
              {name}
            </MenuItem>
          ))}
        </SelectFilter>
      </Grid>
      <Grid size={{ xs:8 }}>
        <SearchTextField
          value={number}
          label={t('Document Number')}
          placeholder="Document Number"
          onChange={(e) => onChange('documentNumber', e.target.value)}
          data-cy="filters-document-number"
          borderRadius="4px 0px 0px 4px"
        />
      </Grid>
    </Grid>
  );
};
