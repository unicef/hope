import React from 'react';
import { TextField } from '@mui/material';

interface TemplateNameOnlineProps {
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
}

export const TemplateNameOnline: React.FC<TemplateNameOnlineProps> = ({
  setFieldValue,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFieldValue('templateName', e.target.value);
  };
  return (
    <TextField
      label="Template Name (optional)"
      variant="outlined"
      fullWidth
      size="medium"
      margin="normal"
      onChange={handleChange}
    />
  );
};
