import {
  FormControl,
  FormHelperText,
  IconButton,
  InputAdornment,
  InputLabel,
  ListItemText,
  MenuItem,
  Select,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import get from 'lodash/get';
import * as React from 'react';
import styled from 'styled-components';

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;
const EndInputAdornment = styled(InputAdornment)`
  margin-right: 10px;
`;

const XIcon = styled(Close)`
  color: #707070;
`;

export function FormikSelectField({
  field,
  form,
  multiple,
  icon = null,
  disableClearable = false,
  ...otherProps
}): React.ReactElement {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const value = multiple
    ? field.value || otherProps.value || []
    : field.value || otherProps.value || '';

  const checkValue = (v): boolean => {
    if (Array.isArray(v)) {
      return v.length > 0;
    }
    return Boolean(v);
  };

  const isValue = checkValue(otherProps.value || field.value);

  const showX = isValue && !disableClearable && !otherProps.disabled;

  return (
    <FormControl variant="outlined" margin="dense" fullWidth {...otherProps}>
      <InputLabel>{otherProps.label}</InputLabel>
      <Select
        {...field}
        {...otherProps}
        name={field.name}
        multiple={multiple}
        value={value}
        id={`textField-${field.name}`}
        error={isInvalid}
        renderValue={(selected) => {
          const selectedItem = otherProps.choices.find(
            (choice) => choice.value === selected || choice.name === selected,
          );

          return selectedItem
            ? selectedItem.labelEn || selectedItem.name || selectedItem.label
            : selected;
        }}
        SelectDisplayProps={{ 'data-cy': `select-${field.name}` }}
        MenuProps={{
          'data-cy': `select-options-${field.name}`,
          getContentAnchorEl: null,
          MenuListProps: { 'data-cy': 'select-options-container' },
        }}
        endAdornment={
          showX && (
            <EndInputAdornment position="end">
              <IconButton
                size="medium"
                onClick={() => {
                  form.setFieldValue(field.name, multiple ? [] : '');
                }}
              >
                <XIcon fontSize="small" />
              </IconButton>
            </EndInputAdornment>
          )
        }
        startAdornment={
          icon ? (
            <StartInputAdornment position="start">{icon}</StartInputAdornment>
          ) : null
        }
      >
        {otherProps.choices.map((each) => (
          <MenuItem
            key={each.value ? each.value : each.name || ''}
            value={each.value ? each.value : each.name || ''}
            data-cy={`select-option-${each.name || each.label}`}
            disabled={each.disabled || false}
          >
            {each.description ? (
              <ListItemText
                primary={each.labelEn || each.name || each.label}
                secondary={each.description}
                primaryTypographyProps={{ noWrap: true }}
                secondaryTypographyProps={{
                  style: { whiteSpace: 'normal', maxWidth: '300px' },
                }}
              />
            ) : (
              each.labelEn || each.name || each.label
            )}
          </MenuItem>
        ))}
      </Select>
      {isInvalid && (
        <FormHelperText error>{get(form.errors, field.name)}</FormHelperText>
      )}
    </FormControl>
  );
}
