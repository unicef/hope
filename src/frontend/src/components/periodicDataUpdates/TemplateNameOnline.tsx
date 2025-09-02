import React from 'react';
import { TextField } from '@mui/material';

interface TemplateNameOnlineProps {
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
  value: string;
}

export const TemplateNameOnline: React.FC<TemplateNameOnlineProps> = ({
  setFieldValue,
  value,
}) => {
  const [error, setError] = React.useState(false);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setError(newValue.length > 0 && newValue.length < 3);
    setFieldValue('name', newValue);
  };
  return (
    <TextField
      label="Template Name (optional)"
      variant="outlined"
      fullWidth
      size="medium"
      margin="normal"
      value={value}
      onChange={handleChange}
      error={error}
      helperText={error ? 'Minimum 3 characters required' : ''}
      slotProps={{ input: { inputProps: { minLength: 3 } } }}
    />
  );
};
