import {
  Box,
  Chip,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
} from '@mui/material';
import { ReactElement } from 'react';

interface Choice {
  value: string;
  name: string;
}

interface FormikChipSelectFieldProps {
  field: { name: string; value: string[] };
  form: { setFieldValue: (name: string, value: any) => void; errors: any; touched: any };
  label?: string;
  choices: Choice[];
  disabled?: boolean;
  lockedValues?: string[];
  [key: string]: any;
}

export function FormikChipSelectField({
  field,
  form,
  label,
  choices,
  disabled,
  lockedValues,
  ...otherProps
}: FormikChipSelectFieldProps): ReactElement {
  const error =
    form.touched[field.name] && form.errors[field.name]
      ? String(form.errors[field.name])
      : undefined;

  const locked = lockedValues ?? [];

  return (
    <FormControl fullWidth variant="outlined" error={!!error} disabled={disabled}>
      {label && (
        <InputLabel id={`${field.name}-label`}>{label}</InputLabel>
      )}
      <Select
        labelId={`${field.name}-label`}
        multiple
        value={field.value || []}
        onChange={(e) => {
          const newValue = e.target.value as string[];
          const missing = locked.filter((v) => !newValue.includes(v));
          form.setFieldValue(field.name, [...newValue, ...missing]);
        }}
        label={label}
        renderValue={(selected: string[]) => (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {selected.map((val) => (
              <Chip
                key={val}
                label={choices.find((c) => c.value === val)?.name || val}
              />
            ))}
          </Box>
        )}
        data-cy={`select-${field.name}`}
        {...otherProps}
      >
        {choices.map((choice) => (
          <MenuItem
            key={choice.value}
            value={choice.value}
            disabled={locked.includes(choice.value)}
          >
            {choice.name}
          </MenuItem>
        ))}
      </Select>
      {error && <FormHelperText>{error}</FormHelperText>}
    </FormControl>
  );
}
