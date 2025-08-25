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
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFieldValue('name', e.target.value);
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
    />
  );
};
