import { Box, Typography } from '@mui/material';
import { ReactElement } from 'react';

interface FormikFileFieldProps {
  field: { name: string };
  form: { setFieldValue: (name: string, value: File | undefined) => void };
  label?: string;
}

export function FormikFileField({ field, form, label }: FormikFileFieldProps): ReactElement {
  return (
    <Box style={{ height: '100%' }} display="flex" flexDirection="column">
      {label && (
        <Typography variant="caption" color="textSecondary" sx={{ mb: 0.5 }}>
          {label}
        </Typography>
      )}
      <Box display="flex" alignItems="center">
        <input
          type="file"
          accept="image/*"
          data-cy={`input-${field.name}`}
          onChange={(event) => {
            form.setFieldValue(field.name, event.currentTarget.files[0]);
          }}
        />
      </Box>
    </Box>
  );
}
